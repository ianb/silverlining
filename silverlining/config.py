import sys
import os
from initools.configparser import ConfigParser
from UserDict import UserDict
import re
import fnmatch
import time
import cPickle as pickle
from cmdutils import CommandError
from libcloud.types import Provider
from libcloud.providers import get_driver as libcloud_get_driver
from silverlining import createconf
from silversupport.env import local_location
from silversupport.appdata import normalize_location


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
            if getattr(self.args, 'debug_libcloud', False):
                print 'XXX', self.args.debug_libcloud, self._driver.connection.conn_classes
                from libcloud.base import LoggingHTTPConnection, LoggingHTTPSConnection
                fp = open(self.args.debug_libcloud, 'a')
                LoggingHTTPConnection.log = LoggingHTTPSConnection.log = fp
                self._driver.connection.conn_classes = (
                    LoggingHTTPConnection, LoggingHTTPSConnection)
        return self._driver

    @property
    def node_hostname(self):
        if getattr(self.args, 'node', None):
            return self.args.node
        if getattr(self.args, 'location'):
            return normalize_location(self.args.location)[0]
        raise CommandError(
            "You must give a --node option")

    def select_image(self, image_match=None, image_id=None, images=None):
        if images is None:
            images = self.cached_images()
        if image_id:
            image_match = 'id %s' % image_id
        if not image_match:
            if self.get('image_id'):
                image_match = 'id %s' % self['image_id']
            elif self.get('image_name'):
                image_match = 'name %s' % self['image_name']
            elif self.get('image'):
                image_match = self['image']
        return self._match('image', image_match, images)

    def select_size(self, size_match=None, size_id=None, sizes=None):
        if sizes is None:
            sizes = self.cached_sizes()
        if size_id:
            size_match = 'id %s' % size_id
        if not size_match:
            if self.get('size_id'):
                size_match = 'id %s' % self['size_id']
            elif self.get('size'):
                size_match = self['size']
        return self._match('size', size_match, sizes)

    def _match(self, type, matcher, items):
        matcher = matcher or ''
        match_pattern = matcher
        if ' ' in matcher:
            match_type, matcher = matcher.split(None, 1)
        else:
            match_type = 'name'
        select_first = False
        if matcher.split()[0] == 'first':
            select_first = True
            matcher = matcher.split(None, 1)[1]
        if not matcher:
            raise LookupError("No matcher available")
        possible = []
        for item in items:
            if match_type == 'id':
                if item.id == matcher:
                    possible.append(item)
            if match_type == 'name':
                if '*' in matcher:
                    if re.match(fnmatch.translate(matcher), item.name, re.I):
                        possible.append(item)
                else:
                    if item.name.lower() == matcher.lower():
                        possible.append(item)
            if match_type == 'ram':
                if self._softint(matcher) == self._softint(item.ram):
                    possible.append(item)
        if not possible:
            raise LookupError(
                "Could not find any %s that matches the pattern %s"
                % (type, match_pattern))
        if select_first:
            if match_type == 'name':
                possible.sort(key=lambda x: x.name.lower())
            elif match_type == 'id':
                possible.sort(key=lambda x: int(x.id))
            elif match_type == 'ram':
                possible.sort(key=lambda x: self._softint(x.ram))
        if not select_first and len(possible) > 1:
            raise LookupError(
                "Multiple %ss matched the pattern %s: %s"
                % (type, match_pattern, ', '.join(repr(i) for i in possible)))
        return possible[0]

    @staticmethod
    def _softint(v):
        if isinstance(v, int):
            return v
        v = re.sub(r'[^\d]', '', v)
        try:
            return int(v)
        except ValueError:
            return None

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

    def cache_object(self, name, expiration=None, driver=None):
        path = local_location(name)
        if os.path.exists(path):
            if expiration is not None:
                age = time.time() - os.path.getmtime(path)
                if age > expiration:
                    return None
            fp = open(path, 'rb')
            obj = pickle.load(fp)
            fp.close()
            if driver:
                for item in obj:
                    item.driver = driver
            return obj
        return None

    def set_cache_object(self, name, obj):
        ## FIXME: some objects are pickleable :(
        path = local_location(name)
        saved = {}
        if isinstance(obj, list):
            for item in obj:
                if getattr(item, 'driver', None):
                    saved[item] = item.driver
                    item.driver = None
        try:
            try:
                fp = open(path, 'wb')
                pickle.dump(obj, fp)
                fp.close()
            except:
                if os.path.exists(path):
                    os.unlink(path)
                raise
        finally:
            for item, driver in saved.iteritems():
                item.driver = driver

    def cached_images(self, expiration=None):
        name = self['provider'] + '-images.cache'
        obj = self.cache_object(name, expiration, driver=self.driver)
        if obj is None:
            obj = self.driver.list_images()
            self.set_cache_object(name, obj)
        return obj

    def cached_sizes(self, expiration=None):
        name = self['provider'] + '-sizes.cache'
        obj = self.cache_object(name, expiration, driver=self.driver)
        if obj is None:
            obj = self.driver.list_sizes()
            self.set_cache_object(name, obj)
        return obj
