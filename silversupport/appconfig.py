import os
import sys
import warnings
from site import addsitedir
from ConfigParser import ConfigParser
from silversupport.env import is_production

class AppConfig(object):

    def __init__(self, config_file, app_name=None):
        if not os.path.exists(config_file):
            raise OSError("No config file %s" % config_file)
        self.config_file = config_file
        parser = ConfigParser()
        parser.read([config_file])
        self.config = {}
        for section in parser.sections():
            for option in parser.options(section):
                self.config.setdefault(section, {})[option] = parser.get(section, option)
        if not is_production():
            if self.config['production'].get('version'):
                warnings.warn('version setting in %s is deprecated' % config_file)
            if self.config['production'].get('default_hostname'):
                warnings.warn('default_hostname setting in %s has been renamed to default_location'
                              % config_file)
        if app_name is None:
            if is_production():
                app_name = os.path.basename(os.path.dirname(config_file)).split('.')[0]
            else:
                app_name = self.config['production']['app_name']
        self.app_name = app_name

    @classmethod
    def from_appinstance(cls, instance_name):
        return cls(os.path.join('/var/www', instance_name, 'app.ini'))

    @property
    def platform(self):
        return self.config['production'].get('platform', 'python')

    @property
    def runner(self):
        filename = self.config['production']['runner']
        return os.path.join(os.path.dirname(self.config_file), filename)

    @property
    def update_fetch(self):
        places = self.config['production'].get('update_fetch')
        if not places:
            return []
        return self.parse_lines(places)

    @property
    def default_location(self):
        return self.config['production'].get('default_location')

    @property
    def services(self):
        services = {}
        c = self.config['production']
        for name in c:
            if name.startswith('service.'):
                services[name[len('service.'):]] = c[name]
        return services

    @property
    def php_root(self):
        return self.config['production'].get('php_root', '/dev/null')

    @property
    def writable_root_location(self):
        if 'service.writable_root' in self.config['production']:
            ## FIXME: do development too
            return os.path.join('/var/lib/silverlining/writable-roots', self.app_name)
        else:
            if is_production():
                return '/dev/null'
            else:
                return ''

    @property
    def app_dir(self):
        return os.path.dirname(self.config_file)

    @property
    def static_dir(self):
        return os.path.join(self.app_dir, 'static')

    @property
    def instance_name(self):
        return os.path.basename(os.path.dirname(self.config_file))

    def parse_lines(self, lines):
        """Parse a configuration value into a series of lines,
        ignoring empty and comment lines"""
        return [
            line.strip() for line in lines.splitlines()
            if line.strip() and not line.strip().startswith('#')]

    def activate_services(self, environ, devel=False, devel_config=None):
        """Activates all the services for this application/configuration.

        Note, this doesn't create databases, this only typically sets
        environmental variables indicating runtime configuration."""
        for service, config in sorted(self.services.items()):
            mod = self.load_service_module(service)
            mod.app_setup(self, config, environ,
                          devel=devel, devel_config=devel_config)

    def load_service_module(self, service_name):
        """Load the service module for the given service name"""
        __import__('silversupport.service.%s' % service_name)
        mod = sys.modules['silversupport.service.%s' % service_name]
        return mod
        
    def activate_path(self):
        """Adds any necessary entries to sys.path for this app"""
        lib_path = os.path.join(
            self.app_dir, 'lib', 'python%s' % sys.version[:3], 'site-packages')
        if lib_path not in sys.path and os.path.exists(lib_path):
            addsitedir(lib_path)
        sitecustomize = os.path.join(
            self.app_dir, 'lib', 'python%s' % sys.version[:3], 'sitecustomize.py')
        if os.path.exists(sitecustomize):
            ns = {'__file__': sitecustomize, '__name__': 'sitecustomize'}
            execfile(sitecustomize, ns)

    def get_app_from_runner(self):
        """Returns the WSGI app that the runner indicates"""
        runner = self.runner
        if '#' in runner:
            runner, spec = runner.split('#', 1)
        else:
            spec = None
        if runner.endswith('.ini'):
            from paste.deploy import loadapp
            from silversupport.secret import get_secret
            runner = 'config:%s' % runner
            global_conf = os.environ.copy()
            global_conf['SECRET'] = get_secret()
            return loadapp(runner, name=spec,
                           global_conf=global_conf)
        elif runner.endswith('.py'):
            ## FIXME: not sure what name to give it
            ns = {'__file__': runner, '__name__': 'main_py'}
            execfile(runner, ns)
            spec = spec or 'application'
            if spec in ns:
                return ns[spec]
            else:
                raise Exception("No application %s defined in %s"
                                % (spec, runner))
        else:
            raise Exception("Unknown kind of runner (%s)" % runner)
        
    def canonical_hostname(self):
        """Returns the 'canonical' hostname for this application.

        This only applies in production environments."""
        from silversupport import appdata
        fp = open(appdata.APPDATA_MAP)
        hostnames = []
        instance_name = self.instance_name
        for line in fp:
            if not line.strip() or line.strip().startswith('#'):
                continue
            hostname, path, data = line.split(None, 2)
            line_instance_name = data.split('|')[0]
            if line_instance_name == instance_name:
                if hostname.startswith('.'):
                    hostname = hostname[1:]
                hostnames.append(hostname)
        hostnames.sort(key=lambda x: len(x))
        if hostnames:
            return hostnames[0]
        else:
            return None
