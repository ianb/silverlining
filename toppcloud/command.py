import os
import fnmatch
import re
import argparse
from UserDict import UserDict
from ConfigParser import ConfigParser
import subprocess
from cmdutils.arg import add_verbose, create_logger
from cmdutils import CommandError
from libcloud.types import Provider
from libcloud.providers import get_driver as libcloud_get_driver
from toppcloud import createconf
from toppcloud import renderscripts
from toppcloud.etchosts import get_host_ip, set_etc_hosts

## The long description of how this command works:
description = """\
Runs a variety of cloud-related commands
"""

parser = argparse.ArgumentParser(
    description=description)

parser.add_argument(
    '-p', '--provider',
    metavar='NAME',
    help="The [provider:NAME] section to use (default [provider:default])",
    default="default")

add_verbose(parser, add_log=True)

subcommands = parser.add_subparsers(dest="command")

parser_list_images = subcommands.add_parser(
    'list-images', help="List all images available")

parser_list_sizes = subcommands.add_parser(
    'list-sizes', help="List all sizes available")

parser_list_nodes = subcommands.add_parser(
    'list-nodes', help="List all active nodes")

parser_destroy = subcommands.add_parser(
    'destroy', help="Destroy the given node")

parser_create = subcommands.add_parser(
    'create', help="Create a new node")

parser_update = subcommands.add_parser(
    'update', help="Update an application")

parser_update.add_argument(
    'dir',
    help="The directory to upload to the server")

parser_update.add_argument(
    '--serve-host',
    metavar="HOST",
    help="Hostname to server off of")

parser_update.add_argument(
    '--site-name',
    metavar="NAME",
    help="'Name' of the site; defaults to directory name")

for host_parser in parser_destroy, parser_create, parser_update:
    host_parser.add_argument(
        '-H', '--host',
        metavar='HOSTNAME',
        help="Hostname of the server/node")

def main():
    if not os.path.exists(createconf.toppcloud_conf):
        print "%s doesn't exists; let's create it" % createconf.toppcloud_conf
        createconf.create_conf()
        return
    args = parser.parse_args()
    create_logger(args)
    config = Config.from_config_file(
        createconf.toppcloud_conf, 'provider:'+args.provider,
        args)
    func = globals()['command_%s' % args.command.replace('-', '_')]
    return func(config)

class Config(UserDict):
    """Represents the configuration, command-line arguments, and
    provider.

    Kind of a holder for all the runtime bits.
    """

    defaults = dict(remote_username='www-mgr')
    
    def __init__(self, config_dict, driver, args=None):
        self.data = config_dict
        for name, value in self.defaults.iteritems():
            self.data.setdefault(name, value)
        self.driver = driver
        self.args = args
        if args:
            self.logger = args.logger

    @classmethod
    def from_config_file(cls, filename, section, args):
        parser = ConfigParser()
        parser.read([filename])
        if not parser.has_section(section):
            args.logger.fatal('No section [%s]' % section)
            args.logger.fatal('Available sections in %s:' % filename)
            for name in parser.sections():
                if name.startswith('provider:'):
                    args.logger.fatal('  [%s] (--provider=%s)'
                                 % (name, name[len('provider:'):]))
            raise CommandError("Bad --provider=%s"
                               % section[len('provider:'):])
        config = {}
        for name in parser.options(section):
            config[name] = parser.get(section, name)
        config['section_name'] = section
        DriverClass = libcloud_get_driver(getattr(Provider, config['provider'].upper()))
        driver = DriverClass(config['username'], config['secret'])
        return cls(config, driver, args=args)

    @property
    def host(self):
        host = self.args.host
        if not host:
            raise CommandError(
                "You must give a --host option")
        host = host.lower()
        return host

    def select_image(self, images=None):
        if images is None:
            images = self.driver.list_images()
        if self.get('image_id'):
            for image in images:
                if image.id == self['image_id']:
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

    def select_size(self, sizes=None):
        if sizes is None:
            sizes = self.driver.list_sizes()
        size_id = self.get('size_id', '').strip()
        for size in sizes:
            if size.id == size_id:
                return size
        raise LookupError("Cannot find any size by the id %r"
                          % size_id)

class App(object):
    """Represents an app to be uploaded/updated"""
    
    def __init__(self, dir, site_name, serve_host):
        self.dir = dir
        self.site_name = site_name
        self.serve_host = serve_host
        parser = ConfigParser()
        assert parser.read([os.path.join(self.dir, 'app.ini')]), (
            "No %s/app.ini found!" % self.dir)
        self.config = {}
        for section in parser.sections():
            self.config[section] = {}
            for option in parser.options(section):
                self.config[section][option] = parser.get(section, option)
        self.version = int(self.config['production']['version'])

    def sync(self, host, app_dir):
        dest_dir = os.path.join('/var/www', app_dir)
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
               self.dir,
               os.path.join('%s:%s' % (host, dest_dir)),
               ]
        proc = subprocess.Popen(cmd)
        proc.communicate()
        
def command_list_images(config):
    images = config.driver.list_images()
    try:
        default_image = config.select_image(images)
    except LookupError:
        default_image = None
    if not default_image:
        config.logger.info(
            '[%s] has no image_id or image_name (default image)' % (
                config['section_name']))
    for image in images:
        if image is default_image:
            default = '**default**'
        else:
            default = ''
        config.logger.notify('%6s %s %s' % (image.id, image.name, default))

def command_list_sizes(config):
    sizes = config.driver.list_sizes()
    try:
        default_size = config.select_size(sizes)
    except LookupError:
        default_size = None
        config.logger.info('[%s] has no size_id (default size)' % (
            config['section_name']))
    for size in sizes:
        if size.id == default_size:
            default = '**default**'
        else:
            default = ''
        config.logger.notify('%s %14s: ram=%5sMb, disk=%3sGb %s' % (
            size.id, size.name, size.ram, size.disk, default))

def command_list_nodes(config):
    for node in config.driver.list_nodes():
        config.logger.notify(
            '%s:%s %6s  %s' % (
                node.name, ' '*(22-len(node.name)), node.state, ', '.join(node.public_ip)))

def command_destroy(config):
    host = config.host
    ## FIXME: should update /etc/hosts
    for node in config.driver.list_nodes():
        if node.name == host:
            config.logger.notify('Destroying node %s' % node.name)
            node.destroy()
            break
    else:
        config.logger.warn('No node found with the name %s' % host)

def command_create(config):
    config.logger.info('Getting image/size info')
    image = config.select_image()
    size = config.select_size()
    files = renderscripts.render_files(config=config)
    config.logger.notify('Creating node (image=%s; size=%s)' % (
        image.name, size.name))
    name = config.host
    assert name, "No --host"
    resp = config.driver.create_node(
        name=name,
        image=image,
        size=size,
        files=files,
        )
    public_ip = resp.public_ip[0]
    config.logger.notify('Status %s at IP %s' % (
        resp.state, public_ip))
    set_etc_hosts(config.logger, config.args.host, public_ip)

_app_dir_re = re.compile(r'app_dir="(.*?)"')

def command_update(config):
    if not os.path.exists(config.args.dir):
        raise CommandError(
            "No directory in %s" % config.args.dir)
    if not config.args.site_name:
        config.args.site_name = os.path.basename(os.path.abspath(config.args.dir))
    if not config.args.serve_host:
        config.args.serve_host = config.host
    app = App(config.args.dir, config.args.site_name, config.args.serve_host)
    ssh_host = '%s@%s' % (config['remote_username'], config.host)
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/prepare-new-site.py %s %s' % (app.site_name, app.version)],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    match = _app_dir_re.search(stdout)
    if not match:
        config.logger.fatal("Did not get the new app_dir from prepare_new_app.py")
        config.logger.fatal("Output: %s" % stdout)
        raise Exception("Bad app_dir output")
    app_dir = match.group(1)
    assert app_dir.startswith(app.site_name)
    app.sync(ssh_host, app_dir)
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/update-hostmap.py %(app_dir)s %(serve_host)s %(version)s.%(serve_host)s; '
         '/var/www/support/update-service.py %(app_dir)s'
         % dict(app_dir=app_dir, serve_host=app.serve_host,
                version=app.version),
         ])
    proc.communicate()
    ip = get_host_ip(config.host)
    set_etc_hosts(config.logger, config.args.serve_host,
                  ip)

if __name__ == '__main__':
    main()

