import os
import sys
import re
from ConfigParser import ConfigParser

SITE_DIR = '/var/www'
HOSTMAP = '/var/www/hostmap.txt'
PLATFORM_MAP = '/var/www/platforms.txt'
PHP_ROOT_MAP = '/var/www/php-roots.txt'
PROCESS_TYPE_MAP = '/var/www/process-types.txt'
WRITABLE_ROOT_MAP = '/var/www/writable-roots.txt'

IGNORE_SITES = set(['default-notfound', 'default-disabled'])

class BadSite(Exception):
    pass

def sites(exclude_ignored=False):
    sites = []
    for name in os.listdir(SITE_DIR):
        if exclude_ignored and name in IGNORE_SITES:
            continue
        if (name != 'support' 
            and os.path.isdir(os.path.join(SITE_DIR, name))):
            sites.append(name)
    return sites

def site_dir(site_name):
    return os.path.join(SITE_DIR, site_name)

def site_config(instance_name):
    app_ini = os.path.join(site_dir(instance_name), 'app.ini')
    parser = ConfigParser()
    if not parser.read([app_ini]):
        raise BadSite('No app.ini in %s' % app_ini)
    return parser

if __name__ == '__main__':
    app_dir = sys.argv[1]
