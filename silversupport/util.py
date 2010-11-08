import os
import string
from ConfigParser import ConfigParser

__all__ = ['unique_name', 'asbool', 'read_config', 'fill_config_environ']


def unique_name(dest_dir, name):
    n = 0
    result = name
    while 1:
        dest = os.path.join(dest_dir, result)
        if not os.path.exists(dest):
            return dest
        n += 1
        result = '%s_%03i' % (name, n)


def asbool(obj, default=ValueError):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            if default is not ValueError:
                return default
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)


def read_config(filename):
    if not os.path.exists(filename):
        raise ValueError('No file %s' % filename)
    parser = ConfigParser()
    parser.read([filename])
    config = {}
    for section in parser.sections():
        for option in parser.options(section):
            config.setdefault(section, {})[option] = parser.get(section, option)
    return config


def fill_config_environ(config, default=''):
    """Fills in configuration values using string.Template
    substitution of environ variables

    If default is KeyError, then empty substitutions will raise KeyError
    """
    vars = _EnvironDict(os.environ, default)

    def fill(value):
        return string.Template(value).substitute(vars)
    config = config.copy()
    _recursive_dict_fill(config, fill)
    return config


def _recursive_dict_fill(obj, filler):
    for key, value in obj.items():
        if isinstance(value, basestring):
            obj[key] = filler(value)
        elif isinstance(value, dict):
            _recursive_dict_fill(value, filler)


class _EnvironDict(object):

    def __init__(self, source, default=''):
        self.source = source
        self.default = default

    def __getitem__(self, key):
        if key in self.source:
            obj = self.source[key]
            if obj is None:
                return ''
            return obj
        if self.default is KeyError:
            raise KeyError(key)
        else:
            return self.default
