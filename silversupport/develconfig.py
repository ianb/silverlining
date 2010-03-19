"""Represents local/development services configuration"""
import os
from ConfigParser import ConfigParser

__all__ = ['silverlining_conf', 'load_devel_config']

silverlining_conf = os.path.join(
    os.environ['HOME'], '.silverlining.conf')


def load_devel_config(app_name):
    """Load all the development configuration specific to this application

    This loads both ``[devel]`` and ``[devel:app_name]`` sections
    (with the latter taking precedence)
    """
    config = {}
    parser = ConfigParser()
    parser.read([silverlining_conf])
    sections = ['devel', 'devel:%s' % app_name]
    for section in sections:
        if not parser.has_section(section):
            continue
        for option in parser.options(section):
            value = parser.get(section, option)
            value = value.replace('APP_NAME', app_name)
            config[option] = value
    return config
