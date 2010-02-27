import os
from ConfigParser import ConfigParser

silverlining_conf = os.path.join(
    os.environ['HOME'], '.silverlining.conf')

def load_devel_config(app_name):
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
