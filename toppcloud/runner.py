import os
import fnmatch
import re
import argparse
from UserDict import UserDict
from initools.configparser import ConfigParser
import subprocess
import virtualenv
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
    help="The [provider:NAME] section from ~/.toppcloud.conf to use (default [provider:default])",
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
    help="The hostname of then node to setup")

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
    '--name',
    metavar="NAME",
    help="'Name' of the site; defaults to directory name")

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

parser_query = subcommands.add_parser(
    'query', help="See what apps and versions are on a node")

parser_query.add_argument(
    '--node',
    metavar='NODE_HOSTNAME',
    help="Node to query")

parser_query.add_argument(
    'site-name', nargs='*',
    help="The site or hostname to query (wildcards allowed)")

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
        DriverClass = libcloud_get_driver(getattr(Provider, config['provider'].upper()))
        driver = DriverClass(config['username'], config['secret'])
        return cls(config, driver, args=args)

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
        parser.read([createconf.toppcloud_conf])
        parser.set(self['section_name'],
                   'default_node', node_name)
        fp = open(createconf.toppcloud_conf, 'w')
        parser.write(fp)
        fp.close()
        self.logger.notify('Set default_node in %s to %s'
                           % (createconf.toppcloud_conf,
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
                config.args.yes = True
                return True
            if response[0] == 'y':
                return True
            if response[0] == 'n':
                return False
            print 'I did not understand the response: %s' % response

class App(object):
    """Represents an app to be uploaded/updated"""
    
    def __init__(self, dir, site_name, host):
        self.dir = dir
        self.site_name = site_name
        self.host = host
        parser = ConfigParser()
        assert parser.read([os.path.join(self.dir, 'app.ini')]), (
            "No %s/app.ini found!" % self.dir)
        self.config = parser.asdict()
        self.version = int(self.config['production']['version'])

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
    try:
        default_node_name = config.node_hostname
    except CommandError:
        default_node_name = None
    for node in config.driver.list_nodes():
        if node.name == default_node_name:
            default = '** default **'
        else:
            default = ''
        config.logger.notify(
            '%s:%s %6s  %15s %s' % (
                node.name, ' '*(22-len(node.name)), node.state,
                ', '.join(node.public_ip), default))

def command_destroy_node(config):
    ## FIXME: This doesn't work at all, wtf?
    for node_hostname in config.args.nodes:
        ## FIXME: should update /etc/hosts
        for node in config.driver.list_nodes():
            if node.name == node_hostname:
                config.logger.notify('Destroying node %s' % node.name)
                node.destroy()
                break
        else:
            config.logger.warn('No node found with the name %s' %
                               node_hostname)

def command_create_node(config):
    config.logger.info('Getting image/size info')
    image = config.select_image(image_id=config.args.image_id)
    size = config.select_size(size_id=config.args.size_id)
    files = renderscripts.render_files(config=config)
    config.logger.notify('Creating node (image=%s; size=%s)' % (
        image.name, size.name))
    node_hostname = config.node_hostname
    if not re.search(r'^[a-z0-9.-]+$', node_hostname):
        raise CommandError(
            "Invalid hostname (must contain only letters, numbers, ., and -): %r"
            % node_hostname)
    assert node_hostname
    resp = config.driver.create_node(
        name=node_hostname,
        image=image,
        size=size,
        files=files,
        )
    public_ip = resp.public_ip[0]
    config.logger.notify('Status %s at IP %s' % (
        resp.state, public_ip))
    set_etc_hosts(config, [node_hostname], public_ip)

def command_default_node(config):
    default_node = config.args.node
    assert default_node
    config.set_default_node(default_node)

def command_setup_node(config):
    os.environ['LANG'] = 'C'
    node = config.args.node
    config.logger.notify(
        'Setting up authentication on server...')
    ssh_host = 'root@%s' % node
    proc = subprocess.Popen([
        'ssh', ssh_host, '''
if [ -e /root/.toppcloud-server-setup ] ; then
    exit 50
fi
mkdir -p /root/.ssh
cat >> /root/.ssh/authorized_keys
''',
        ], stdin=subprocess.PIPE)
    key = open(os.path.join(os.environ['HOME'],
                            '.ssh', 'id_dsa.pub'), 'rb').read()
    proc.communicate(key)
    # if proc.returncode == 50:
    #     config.logger.fatal(
    #         "The server has already been setup (/root/.toppcloud-server-setup exists)")
    #     return 2
    config.logger.notify(
        "Updating indexes and setting up rsync")
    proc = subprocess.Popen([
        'ssh', ssh_host, '''
apt-get update -qq
apt-get -y -q install rsync
''',
        ])
    proc.communicate()
    if proc.returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 3
    setup_rsync(config, 'root', '/root/')
    config.logger.notify(
        "Running apt-get install on server")
    lines = list(open(os.path.join(os.path.dirname(__file__),
                                   'server-files',
                                   'dpkg-query.txt')))
    packages = ' '.join(line.strip().split()[0]
                        for line in lines
                        if line.strip())
    proc = subprocess.Popen([
        'ssh', ssh_host,
        'apt-get -y -q=2 install $(cat)'],
                            stdin=subprocess.PIPE)
    proc.communicate(packages)
    if proc.returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 5
    
    setup_rsync(config, 'serverroot/', '/')
    setup_script = open(os.path.join(os.path.dirname(__file__),
                                     'server-files',
                                     'update-server-script.sh')).read()
    import getpass
    username = getpass.getuser()
    setup_script = setup_script.replace('__REMOTE_USER__', username)
    
    proc = subprocess.Popen(
        ['ssh', ssh_host, setup_script])
    proc.communicate()
    if proc.returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % proc.returncode)
        # No need to ask because it's the last task anyway
        return 6

def setup_rsync(config, source, dest):
    cwd = os.path.join(os.path.dirname(__file__), 'server-files')
    proc = subprocess.Popen([
        'rsync', '--quiet', '-rvC',
        source, 'root@%s:%s' % (config.args.node, dest)],
                            cwd=cwd)
    config.logger.notify(
        "rsyncing %s to %s" % (source, dest))
    proc.communicate()
    if proc.returncode:
        config.logger.fatal(
            "An error occurred in rsync (code=%s)" % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            raise CommandError(
                "Aborting due to failure")

_instance_name_re = re.compile(r'app_dir="(.*?)"')

def command_update(config):
    if not os.path.exists(config.args.dir):
        raise CommandError(
            "No directory in %s" % config.args.dir)
    if not config.args.name:
        config.args.name = os.path.basename(os.path.abspath(config.args.dir))
        config.logger.info('Using app name=%r' % config.args.name)
    config.logger.info('Fixing up .pth and .egg-info files')
    virtualenv.logger = config.logger
    virtualenv.fixup_pth_and_egg_link(
        config.args.dir,
        [os.path.join(config.args.dir, 'lib', 'python2.6'),
         os.path.join(config.args.dir, 'lib', 'python2.6', 'site-packages'),
         os.path.join(config.args.dir, 'lib', 'python')])
    app = App(config.args.dir, config.args.name, config.args.host)
    if not config.args.host:
        if app.config['production'].get('default_host'):
            config.args.host = app.config['production']['default_host']
        else:
            config.args.host = config.node_hostname
    ssh_host = '%s@%s' % (config['remote_username'], config.node_hostname)
    ssh_root_host = 'root@%s' % config.node_hostname
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/prepare-new-site.py %s %s' % (app.site_name, app.version)],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    match = _instance_name_re.search(stdout)
    if not match:
        config.logger.fatal("Did not get the new instance_name from prepare-new-site.py")
        config.logger.fatal("Output: %s" % stdout)
        raise Exception("Bad instance_name output")
    instance_name = match.group(1)
    assert instance_name.startswith(app.site_name)
    app.sync(ssh_host, instance_name)
    proc = subprocess.Popen(
        ['ssh', ssh_root_host,
         'python -m compileall -q /var/www/%(instance_name)s; '
         '/var/www/support/update-service.py %(instance_name)s'
         % dict(instance_name=instance_name),
         ])
    proc.communicate()

    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/update-hostmap.py %(instance_name)s %(host)s %(version)s.%(host)s; '
         'sudo -u www-data /var/www/support/internal-request.py update %(instance_name)s %(host)s; '
         'sudo -u www-data pkill -INT -f -u www-data wsgi; '
         % dict(instance_name=instance_name,
                host=config.args.host,
                version=app.version),
         ])
    proc.communicate()

    ip = get_host_ip(config.node_hostname)
    set_etc_hosts(config, [config.args.host,
                           '%s.%s' % (app.version, config.args.host),
                           'prev.' + config.args.host], ip)

def command_init(config):
    import sys
    dir = config.args.dir
    app_name = os.path.basename(os.path.abspath(dir))
    vars = dict(
        app_name=app_name,
        main=config.args.main,
        config=config.args.config)
    vars['force'] = config.args.force
    if sys.version[:3] == '2.6':
        virtualenv.logger = config.logger
        virtualenv.create_environment(
            dir,
            # This should be true to pick up global binaries like psycopg:
            site_packages=True,
            unzip_setuptools=True,
            use_distribute=config.args.distribute)
    else:
        # This is the crude way we need to do this when we're not in Python 2.6
        config.logger.warn('Creating virtualenv environment in subprocess')
        virtualenv_file = virtualenv.__file__
        if virtualenv_file.endswith('.pyc'):
            virtualenv_file = virtualenv_file[:-1]
        if config.args.distribute:
            cmd = [
                'python2.6', virtualenv_file,
                '--unzip-setuptools', '--distribute',
                dir]
        else:
            cmd = [
                'python2.6', virtualenv_file,
                '--unzip-setuptools', dir]
        proc = subprocess.Popen(cmd)
        proc.communicate()
    noforce_vars = vars.copy()
    noforce_vars['force'] = False
    init_copy('README.txt', os.path.join(dir, 'README.txt'), config.logger, noforce_vars)
    init_copy('app.ini', os.path.join(dir, 'app.ini'), config.logger, noforce_vars)
    if config.args.config:
        init_copy('config.ini', os.path.join(dir, 'config.ini'), config.logger, vars)
    if config.args.main:
        init_copy('main.py', os.path.join(dir, 'main.py'), config.logger, vars)
    src = os.path.join(dir, 'src')
    if not os.path.exists(src):
        os.mkdir(src)
    static = os.path.join(dir, 'static')
    if not os.path.exists(static):
        os.mkdir(static)
    lib_python = os.path.join(dir, 'lib', 'python')
    if not os.path.exists(lib_python):
        os.makedirs(lib_python)
    init_copy(
        'sitecustomize.py',
        os.path.join(dir, 'lib', 'python2.6', 'sitecustomize.py'),
        config.logger, vars)
    init_copystring(
        _distutils_cfg,
        os.path.join(dir, 'lib', 'python2.6', 'distutils', 'distutils.cfg'),
        config.logger, vars, append=True)
    init_copystring(
        _distutils_init,
        os.path.join(dir, 'lib', 'python2.6', 'distutils', '__init__.py'),
        config.logger, vars, append=True)

_distutils_cfg = """\
# This is what makes things install into lib/python instead of lib/python2.6:
[install]
home = <sys.prefix>
"""

_distutils_init = """\

# Patch by toppcloud:
old_parse_config_files = dist.Distribution.parse_config_files
def parse_config_files(self, filenames=None):
    old_parse_config_files(self, filenames)
    opt_dict = self.get_option_dict('install')
    if 'home' in opt_dict:
        location, value = opt_dict['home']
        if value.lower().strip() == 'default':
            del opt_dict['home']
        else:
            opt_dict['home'] = (location, value.replace('<sys.prefix>', sys.prefix))
dist.Distribution.parse_config_files = parse_config_files
"""

def init_copy(source, dest, logger, vars, append=False):
    import tempita
    source = os.path.join(
        os.path.dirname(__file__),
        'init-files',
        source)
    if os.path.exists(source+'.tmpl'):
        source = source+'.tmpl'
        template = tempita.Template.from_filename(source)
        source_content = template.substitute(vars)
    else:
        fp = open(source, 'rb')
        source_content = fp.read()
        fp.close()
    init_copystring(source_content, dest, logger, vars,
                    append=append)

def init_copystring(source_content, dest, logger, vars,
                    append=False):
    if os.path.exists(dest):
        fp = open(dest, 'rb')
        content = fp.read()
        fp.close()
        if append:
            if content in source_content:
                logger.info(
                    'Not adding to %s (already has content)' % dest)
                return
        else:
            if content == source_content:
                logger.info(
                    'Not overwriting %s (same content)' % dest)
                return
            elif vars['force']:
                logger.notify(
                    'Overwriting %s' % dest)
            else:
                logger.notify(
                    'Not overwriting %s (content differs)' % dest)
                return
    if append:
        fp = open(dest, 'ab')
    else:
        fp = open(dest, 'wb')
    fp.write(source_content)
    fp.close()

def command_serve(config):
    from toppcloud import server
    server.serve(config)

def command_clean_node(config):
    ssh_host = '%s@%s' % (config['remote_username'],
                          config.node_hostname)
    if config.args.simulate:
        simulate = '-n'
    else:
        simulate = ''
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/cleanup-apps.py %s' % simulate])
    proc.communicate()
        
def command_query(config):
    proc = subprocess.Popen(
        ['ssh', '%s@%s' % (config['remote_username'], config.node_hostname),
         'cat /var/www/hostmap.txt; echo "END" ; ls /var/www'],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    hosts = {}
    lines = [line.strip()
             for line in stdout.splitlines()
             if line.strip() and not line.strip().startswith('#')]
    hosts = {}
    site_instances = {}
    instance_site = {}
    sites = set()
    while 1:
        if not lines:
            break
        line = lines.pop(0)
        if line == 'END':
            break
        hostname, sitename = line.split(None, 1)
        hosts[hostname] = sitename
    for line in lines:
        match = re.match(r'^(?:([a-z0-9_.-]+)\.(\d+)\.(.*)|default-[a-z]+)$',
                         line)
        if not match:
            continue
        if not match.group(1):
            site_name = line
            version = ''
            release = ''
        else:
            site_name = match.group(1)
            version = match.group(2)
            release = match.group(3)
        site_instances.setdefault(site_name, {})[(version, release)] = line
        sites.add(site_name)
        instance_site[line] = site_name
    site_names = getattr(config.args, 'site-name')
    if site_names:
        matcher = re.compile('|'.join(fnmatch.translate(s) for s in site_names))
        new_hosts = {}
        new_site_instances = {}
        new_instance_site = {}
        new_sites = set()
        for site in sites:
            if matcher.match(site):
                new_sites.add(site)
        for hostname, instance in hosts.iteritems():
            if matcher.match(hostname):
                new_sites.add(instance.split('.')[0])
        for site in new_sites:
            new_site_instances[site] = site_instances[site]
            for n, v in instance_site.iteritems():
                if v == site:
                    new_instance_site[n] = v
            for n, v in hosts.iteritems():
                if v.startswith(site):
                    new_hosts[n] = v
        hosts = new_hosts
        site_instances = new_site_instances
        instance_site = new_instance_site
        sites = new_sites
    info = config.logger.info
    notify = config.logger.notify
    for site in sorted(sites):
        if len(sites) > 1:
            notify('Site: %s' % site)
            config.logger.indent += 2
        try:
            for (version, release), instance_name in sorted(site_instances[site].items()):
                hostnames = []
                for hostname, inst in hosts.items():
                    if ':' in hostname:
                        # boring
                        continue
                    if hostname.startswith('www.'):
                        continue
                    if inst == instance_name:
                        hostnames.append(hostname)
                if not hostnames:
                    notify('%s (defunct instance)' % instance_name)
                elif len(hostnames) == 1:
                    notify('%s: %s' % (instance_name, hostnames[0]))
                else:
                    notify('%s:' % instance_name)
                    for hostname in sorted(hostnames):
                        notify('  %s' % hostname)
        finally:
            if len(sites) > 1:
                config.logger.indent -= 2
                

if __name__ == '__main__':
    main()
