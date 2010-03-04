"""silverlining interface

This implements the command-line interface of silverlining.  It includes
all the commands and their options, though the implementation of the
commands are in silverlining.commands.*

There are also a few shared objects implemented here, specifically
`Config` and `App`
"""

import os
import sys
import fnmatch
import re
import argparse
from UserDict import UserDict
from initools.configparser import ConfigParser
import subprocess
from cmdutils.arg import add_verbose, create_logger
from cmdutils import CommandError
from libcloud.types import Provider
from libcloud.providers import get_driver as libcloud_get_driver
from silverlining import createconf

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
    '--image-id',
    metavar="ID",
    help="Image ID to use")

parser_create.add_argument(
    '--size-id',
    metavar="ID",
    help="Size ID to use")

parser_create.add_argument(
    '--setup-node', action='store_true',
    help="Wait for the node to be created (this means the command just "
    "sits for a couple minutes) and then set up the server.  It is suggested "
    "you also use --yes with this option.")

parser_default = subcommands.add_parser(
    'default-node', help="Set a node as the default node")

parser_default.add_argument(
    'node',
    metavar='HOSTNAME',
    help="The hostname of the node to set as default")

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
    '--host', '-H',
    metavar="HOST",
    help="Hostname to server off of")

parser_update.add_argument(
    '--debug-single-process',
    action='store_true',
    help="Install as a 'debug' application, running in a single process with "
    "threads, so the application can be used with weberror or other debug "
    "tools.")

parser_update.add_argument(
    '--name',
    metavar="NAME",
    help="'Name' of the site; defaults to app_name")

parser_update.add_argument(
    '--node',
    metavar='NODE_HOSTNAME',
    help="The hostname of the node to upload to")

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
    help="Use config.ini (not main.py)")

parser_init.add_argument(
    '--main',
    action='store_true',
    help="Use main.py (not config.ini)")    

parser_serve = subcommands.add_parser(
    'serve', help="Serve up an application for development")

parser_serve.add_argument(
    'dir',
    metavar='APP_DIR',
    help='Directory holding app')

## We can't handle silverlining run well with a subparser, because
## there's a bug in subparsers that they can't ignore arguments they
## don't understand.  Because there will be arguments passed to the
## remote command we need that, so instead we create an entirely
## separate parser, and we'll do a little checking to see if the run
## command is given:

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
    'host',
    help="Host where the application is running")

parser_run.add_argument(
    'script',
    help="script (in bin/) to run")

parser_run.add_argument(
    '--user', metavar='USERNAME',
    default="www-data",
    help="The user to run the command as; default is www-data.  "
    "Other options are www-mgr and root")

parser_query = subcommands.add_parser(
    'query', help="See what apps and versions are on a node")

parser_query.add_argument(
    '--node',
    metavar='NODE_HOSTNAME',
    help="Node to query")

parser_query.add_argument(
    'site-name', nargs='*',
    help="The site or hostname to query (wildcards allowed)")

parser_activate = subcommands.add_parser(
    'activate', help="Activate a site instance for a given domain")

parser_activate.add_argument(
    '--node',
    metavar="NODE_HOSTNAME",
    help="Node to act on")

parser_activate.add_argument(
    'host',
    help="The hostname to act on")

parser_activate.add_argument(
    'instance_name',
    help="The instance name to activate (can also be a version number or \"prev\")")

parser_deactivate = subcommands.add_parser(
    'deactivate', help="Deactivate a site (leaving it dangling)")

parser_deactivate.add_argument(
    '--node',
    metavar="NODE_HOSTNAME",
    help="Node to act on")

parser_deactivate.add_argument(
    'hosts', nargs='+',
    help="The hostname to act on; if you give more than one, "
    "they must all be on the same node")

parser_deactivate.add_argument(
    '--disable', action='store_true',
    help="Set the host to the status disabled, pointing it at the disabled application (good for a temporary removal)")

parser_deactivate.add_argument(
    '--keep-prev', action='store_true',
    help="Keep the prev.* host activate (by default it is deleted)")

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

class Config(UserDict):
    """Represents the configuration, command-line arguments, and
    provider.

    Kind of a holder for all the runtime bits.
    """
    ## FIXME: refactoring this (and App) would be excellent

    ## FIXME: the one and only default configuration; this should be
    ## converted to be hardcoded:
    defaults = dict(remote_username='www-mgr')
    
    def __init__(self, config_dict, args=None):
        self.data = config_dict
        for name, value in self.defaults.iteritems():
            self.data.setdefault(name, value)
        self._driver = None
        self.args = args
        if args:
            self.logger = args.logger

    @classmethod
    def from_config_file(cls, filename, section, args):
        """Instantiate from a configuration file"""
        parser = ConfigParser()
        parser.read([filename])
        full_config = parser.asdict()
        if section not in full_config:
            args.logger.fatal('No section [%s]' % section)
            args.logger.fatal('Available sections in %s:' % filename)
            for name in full_config:
                if name.startswith('provider:'):
                    args.logger.fatal('  [%s] (--provider=%s)'
                                 % (name, name[len('provider:'):]))
            raise CommandError("Bad --provider=%s"
                               % section[len('provider:'):])
        config = full_config[section]
        config['section_name'] = section
        return cls(config, args=args)

    @property
    def driver(self):
        if self._driver is None:
            provider = self['provider']
            DriverClass = libcloud_get_driver(getattr(Provider, provider.upper()))
            self._driver = DriverClass(self['username'], self['secret'])
        return self._driver

    @property
    def node_hostname(self):
        if getattr(self.args, 'node', None):
            return self.args.node
        if self.get('default_node'):
            return self['default_node']
        raise CommandError(
            "You must give a --node option or set default-node")

    def select_image(self, images=None, image_id=None):
        if images is None:
            images = self.driver.list_images()
        if image_id or self.get('image_id'):
            image_id = image_id or self['image_id']
            for image in images:
                if image.id == image_id:
                    return image
            else:
                raise LookupError(
                    "No image with the id %s" % self['image_id'])
        elif self.get('image_name'):
            image_name = self['image_name']
            if '*' in image_name:
                regex = re.compile(fnmatch.translate(image_name))
                images = sorted(
                    [image for image in images
                     if regex.match(image.name)],
                    key=lambda i: i.name)
                if not images:
                    raise LookupError(
                        "No image matches the pattern %s" % image_name)
                return images[-1]
            else:
                for image in images:
                    if image.name == image_name:
                        return image
                else:
                    raise LookupError(
                        "No image with the name %s" % image_name)
        else:
            raise LookupError(
                "No config for image_id or image_name")

    def select_size(self, sizes=None, size_id=None):
        if sizes is None:
            sizes = self.driver.list_sizes()
        size_id = size_id or self.get('size_id', '').strip()
        for size in sizes:
            if size.id == size_id:
                return size
        raise LookupError("Cannot find any size by the id %r"
                          % size_id)

    def set_default_node(self, node_name):
        parser = ConfigParser()
        parser.read([createconf.silverlining_conf])
        parser.set(self['section_name'],
                   'default_node', node_name)
        fp = open(createconf.silverlining_conf, 'w')
        parser.write(fp)
        fp.close()
        self.logger.notify('Set default_node in %s to %s'
                           % (createconf.silverlining_conf,
                              node_name))

    def ask(self, query):
        if getattr(self.args, 'yes', False):
            self.logger.warn(
                "%s YES [auto]" % query)
            return True
        while 1:
            response = raw_input(query+" [y/n] ")
            response = response.strip().lower()
            if not response:
                continue
            if 'all' in response and response[0] == 'y':
                self.args.yes = True
                return True
            if response[0] == 'y':
                return True
            if response[0] == 'n':
                return False
            print 'I did not understand the response: %s' % response

    def run(self, command, stdin=None, return_stdout=False,
            set_env=None, cwd=None):
        env = os.environ.copy()
        env['LANG'] = 'C'
        if set_env:
            env.update(set_env)
        def _quote(arg):
            if ' ' in arg:
                return "%s" % arg.replace('"', '\\"')
            return arg
        command_text = ' '.join(
            _quote(arg) for arg in command)
        self.logger.debug("Calling: %s" % command_text)
        kw = {}
        if stdin:
            kw['stdin'] = subprocess.PIPE
        if return_stdout:
            kw['stdout'] = subprocess.PIPE
        if cwd:
            kw['cwd'] = cwd
        proc = subprocess.Popen(
            command, env=env, **kw)
        stdout, stderr = proc.communicate(stdin)
        if proc.returncode:
            self.logger.info('Error calling %s' % command_text)
            self.logger.info('Return code: %s' % proc.returncode)
        return stdout, proc.returncode

class App(object):
    """Represents an app to be uploaded/updated"""
    
    def __init__(self, dir, site_name, host):
        if not dir.endswith('/'):
            dir += '/'
        self.dir = dir
        self.host = host
        parser = ConfigParser()
        assert parser.read([os.path.join(self.dir, 'app.ini')]), (
            "No %s/app.ini found!" % self.dir)
        self.config = parser.asdict()
        self.version = int(self.config['production']['version'])
        if not site_name:
            site_name = self.config['production']['app_name']
        self.site_name = site_name

    def sync(self, host, instance_name):
        dest_dir = os.path.join('/var/www', instance_name)
        exclude_from = os.path.join(os.path.dirname(__file__), 'rsync-exclude.txt')
        cmd = ['rsync',
               '--recursive',
               '--links',         # Copy over symlinks as symlinks
               '--safe-links',    # Don't copy over links that are outside of dir
               '--executability', # Copy +x modes
               '--times',         # Copy timestamp
               '--rsh=ssh',       # Use ssh
               '--delete',        # Delete files thta aren't in the source dir
               '--compress',
               #'--skip-compress=.zip,.egg', # Skip some already-compressed files
               '--exclude-from=%s' % exclude_from,
               '--progress',
               '--quiet',
               self.dir,
               os.path.join('%s:%s' % (host, dest_dir)),
               ]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        
if __name__ == '__main__':
    main()

