import os
from ConfigParser import ConfigParser

__all__ = ['unique_name', 'asbool']


def unique_name(dest_dir, name):
    n = 0
    result = name
    while 1:
        dest = os.path.join(dest_dir, result)
        if not os.path.exists(dest):
            return dest
        n += 1
        result = '%s_%03i' % (name, n)

def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
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
