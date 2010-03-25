import sys
from initools.configparser import ConfigParser
from UserDict import UserDict
from cmdutils import CommandError
from libcloud.types import Provider
from libcloud.providers import get_driver as libcloud_get_driver
import re
import fnmatch
from silverlining import createconf


class Config(UserDict):
    """Represents the configuration, command-line arguments, and
    provider.
    """

    def __init__(self, config_dict, args=None):
        self.data = config_dict
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
            if ':' in provider:
                # Then it's a module import path
                mod, obj_name = provider.split(':', 1)
                __import__(mod)
                mod = sys.modules[mod]
                DriverClass = getattr(mod, obj_name)
            else:
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
