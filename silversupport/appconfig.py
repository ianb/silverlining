import os
from ConfigParser import ConfigParser

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
        if app_name is None:
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
            return '/dev/null'

    def parse_lines(self, lines):
        return [
            line.strip() for line in lines.splitlines()
            if line.strip() and not line.strip().startswith('#')]
