"""silverlining interface

This implements the command-line interface of silverlining.  It includes
all the commands and their options, though the implementation of the
commands are in ``silverlining.commands.*``
"""

import os
import sys
import argparse
from cmdutils.arg import add_verbose, create_logger
from cmdutils import CommandError
from silverlining import createconf
from silverlining.config import Config


## Following is a HUGE BLOCK of argument definitions:

## The long description of how this command works:
description = """\
Runs a variety of cloud-related commands
"""

parser = argparse.ArgumentParser(
    description=description)

## FIXME: these options should also be available in the subparsers:
parser.add_argument(
    '-p', '--provider',
    metavar='NAME',
    help="The [provider:NAME] section from ~/.silverlining.conf to use (default [provider:default])",
    default="default")

parser.add_argument(
    '-y', '--yes',
    action='store_true',
    help="Answer yes to any questions")

add_verbose(parser, add_log=True)

subcommands = parser.add_subparsers(dest="command")

parser_list_images = subcommands.add_parser(
    'list-images', help="List all images available")

parser_list_sizes = subcommands.add_parser(
    'list-sizes', help="List all sizes available")

parser_list_nodes = subcommands.add_parser(
    'list-nodes', help="List all active nodes")

parser_destroy = subcommands.add_parser(
    'destroy-node', help="Destroy a node")

parser_destroy.add_argument(
    'nodes', nargs='+',
    metavar='HOSTNAME',
    help="The hostname(s) of the node to destroy")

parser_create = subcommands.add_parser(
    'create-node', help="Create a new node")

parser_create.add_argument(
    'node',
    metavar='HOSTNAME',
    help="The hostname of the node to create")

parser_create.add_argument(
    '--image',
    default='name *karmic*',
    metavar="IMAGE",
    help='Image to use, can be "id 10", and can contain wildcards like "name *karmic*".  '
    'Default is "name *karmic*" which will select an Ubuntu Karmic image.')

parser_create.add_argument(
    '--size',
    metavar="SIZE",
    default="ram 256",
    help='Size to use, can be "id 1", "ram 256" etc')

parser_create.add_argument(
    '--setup-node', action='store_true',
    help="Wait for the node to be created (this means the command just "
    "sits for a couple minutes) and then set up the server.  It is suggested "
    "you also use --yes with this option.")

parser_create.add_argument(
    '--wait', action='store_true',
    help="Wait for the node to be created, but don't setup (like "
    "--setup-node that just quits before it actually sets up the node)")

parser_create.add_argument(
    '--if-not-exists', action='store_true',
    dest='if_not_exists',
    help="Only create the node if it does not exist (will check the cloud "
    "providers server list)")

parser_setup = subcommands.add_parser(
    'setup-node', help="Setup a new (fresh Ubuntu Jaunty install) server")

parser_setup.add_argument(
    'node',
    metavar='HOSTNAME',
    help="The hostname of the node to setup")

parser_clean = subcommands.add_parser(
    'clean-node', help="Clean unused application instances on a node")

parser_clean.add_argument(
    'node', nargs='?',
    metavar='HOSTNAME',
    help="Node to clean instances from")

parser_clean.add_argument(
    '-n', '--simulate',
    action='store_true',
    help="Don't actually clean anything, just show what would be done")

parser_update = subcommands.add_parser(
    'update', help="Update/deploy an application")

parser_update.add_argument(
    'dir',
    help="The directory to upload to the server")

parser_update.add_argument(
    'location', nargs='?',
    metavar="HOSTNAME[/PATH]",
    help="Place to upload to (will default to the default_location "
    "setting in app.ini)")

parser_update.add_argument(
    '--debug-single-process',
    action='store_true',
    help="Install as a 'debug' application, running in a single process with "
    "threads, so the application can be used with weberror or other debug "
    "tools.")

parser_update.add_argument(
    '--name',
    metavar="NAME",
    help="'Name' of the site; defaults to the app_name setting in app.ini")

parser_update.add_argument(
    '--node',
    metavar='NODE_HOSTNAME',
    help="The hostname of the node to upload to")

parser_update.add_argument(
    '--clear',
    action='store_true',
    help='Clear the database on update (clears all database, files, etc!)')

parser_init = subcommands.add_parser(
    'init', help="Create a new application file layout")

parser_init.add_argument(
    'dir',
    metavar='DIR',
    help="A directory to initialize")

parser_init.add_argument(
    '-f', '--force',
    action='store_true',
    help="Overwrite files even if they already exist")

parser_init.add_argument(
    '--distribute',
    action='store_true',
    help="Use Distribute (instead of Setuptools)")

parser_init.add_argument(
    '--config',
    action='store_true',
    help="Put in a sample Paste Deploy config.ini")

parser_init.add_argument(
    '--main',
    action='store_true',
    help="Put in a sample main.py")

parser_serve = subcommands.add_parser(
    'serve', help="Serve up an application for development")

parser_serve.add_argument(
    'dir',
    metavar='APP_DIR',
    help='Directory holding app')

## We can't handle "silver run" well with a subparser, because there's
## a bug in subparsers that they can't ignore arguments they don't
## understand.  Because there will be arguments passed to the remote
## command we need that, so instead we create an entirely separate
## parser, and we'll do a little checking to see if the run command is
## given:

parser_run = argparse.ArgumentParser(
    add_help=False,
    description="""\
Run a command for an application; this runs a script in bin/ on the
remote server.

Use it like:
    silver run import-something --option-for-import-something

Note any arguments that point to existing files or directories will
cause those files/directories to be uploaded, and substituted with the
location of the remote name.
""")

parser_run.add_argument(
    '-p', '--provider',
    metavar='NAME',
    help="The [provider:NAME] section from ~/.silverlining.conf to use (default [provider:default])",
    default="default")

parser_run.add_argument(
    '-y', '--yes',
    action='store_true',
    help="Answer yes to any questions")

#add_verbose(parser_run, add_log=True)

parser_run.add_argument(
    'location',
    help="Location where the application is running")

parser_run.add_argument(
    'script',
    help="script (in bin/) to run")

parser_run.add_argument(
    '--user', metavar='USERNAME',
    default="www-data",
    help="The user to run the command as; default is www-data.  "
    "Other options are www-mgr and root")

parser_query = subcommands.add_parser(
    'query', help="See what apps are on a node")

parser_query.add_argument(
    'node',
    metavar='HOSTNAME',
    help="Node to query")

parser_query.add_argument(
    'app-name', nargs='*',
    help="The app_name or hostname to query (wildcards allowed)")

parser_activate = subcommands.add_parser(
    'activate', help="Activate a site instance for a given domain")

parser_activate.add_argument(
    '--node',
    metavar="NODE_HOSTNAME",
    help="Node to act on")

parser_activate.add_argument(
    'location',
    help="The hostname/path to act on")

parser_activate.add_argument(
    'instance_name',
    help="The instance name to activate (can also be \"prev\")")

parser_deactivate = subcommands.add_parser(
    'deactivate', help="Deactivate a site (leaving it dangling)")

parser_deactivate.add_argument(
    '--node',
    metavar="NODE_HOSTNAME",
    help="Node to act on")

parser_deactivate.add_argument(
    'locations', nargs='+',
    help="The hostname/path to act on; if you give more than one, "
    "they must all be on the same node.  Can be a wildcard.")

parser_deactivate.add_argument(
    '--disable', action='store_true',
    help="Set the host to the status disabled, pointing it at the disabled application (good for a temporary removal)")

parser_deactivate.add_argument(
    '--keep-prev', action='store_true',
    help="Keep the prev.* host activate (by default it is deleted)")

# This is a mock for use with -h:
parser_run_mock = subcommands.add_parser(
    'run', help="Run a command on a remote host")

parser_run_mock.add_argument(
    '-p', '--provider',
    metavar='NAME',
    help="The [provider:NAME] section from ~/.silverlining.conf to use (default [provider:default])",
    default="default")

parser_run_mock.add_argument(
    '-y', '--yes',
    action='store_true',
    help="Answer yes to any questions")

#add_verbose(parser_run, add_log=True)

parser_run_mock.add_argument(
    'host',
    help="Host where the application is running")

parser_run_mock.add_argument(
    'script',
    help="script (in bin/) to run")

parser_run_mock.add_argument(
    '--user', metavar='USERNAME',
    default="www-data",
    help="The user to run the command as; default is www-data.  "
    "Other options are www-mgr and root")

parser_backup = subcommands.add_parser(
    'backup', help="Backup a deployed application's data")

parser_backup.add_argument(
    'location', metavar="LOCATION",
    help="The location to back up (i.e., the server and application)")

parser_backup.add_argument(
    'destination', metavar='DESTINATION',
    help="Destination to back up to.  Can be a local file, remote:filename, "
    "site://location, ssh://hostname/location rsync://hostname/location")

parser_restore = subcommands.add_parser(
    'restore', help="Restore a backup")

parser_restore.add_argument(
    'backup', metavar="BACKUP",
    help="The backup to restore (file or archive)")

parser_restore.add_argument(
    'location', metavar="LOCATION",
    help="Location (hostname[/path]) to restore to")

parser_clear = subcommands.add_parser(
    'clear', help="Clear the data from an app")

parser_clear.add_argument(
    'location', metavar="LOCATION",
    help="Location (hostname[/path]) to clear")

parser_diff = subcommands.add_parser(
    'diff', help="Diff a local app and a deployed app")

parser_diff.add_argument(
    'dir', metavar='DIR',
    help="The application to diff")

parser_diff.add_argument(
    'location', metavar='HOST', nargs='?',
    help="the host to diff with")

parser_diff.add_argument(
    '--app-name', metavar='NAME',
    help="A name besides app.ini:app_name")

parser_diff.add_argument(
    '--instance-name', metavar='APP_NAME.DATE_VERSION',
    help="Diff with a specific instance (not the active one)")

def catch_error(func):
    """Catch CommandError and turn it into an error message"""
    def decorated(*args, **kw):
        try:
            return func(*args, **kw)
        except CommandError, e:
            print e
            sys.exit(2)
    return decorated


@catch_error
def main():
    if not os.path.exists(createconf.silverlining_conf):
        print "%s doesn't exists; let's create it" % createconf.silverlining_conf
        createconf.create_conf()
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        # Special case for silver run:
        if sys.argv[2:] in [['-h'], ['--help']]:
            # Don't generally catch this, as you might want to pass this option
            print parser_run.format_help()
            return 0
        args, unknown_args = parser_run.parse_known_args(sys.argv[2:])
        args.unknown_args = unknown_args
        args.command = 'run'
    else:
        args = parser.parse_args()
    create_logger(args)
    config = Config.from_config_file(
        createconf.silverlining_conf, 'provider:'+args.provider,
        args)
    name = args.command.replace('-', '_')
    mod_name = 'silverlining.commands.%s' % name
    __import__(mod_name)
    mod = sys.modules[mod_name]
    func = getattr(mod, 'command_%s' % name)
    return func(config)


if __name__ == '__main__':
    main()
