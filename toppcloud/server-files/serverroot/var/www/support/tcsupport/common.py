import os
import sys
from ConfigParser import ConfigParser

SITE_DIR = '/var/www'
HOSTMAP = '/var/www/hostmap.txt'
PLATFORM_MAP = '/var/www/platforms.txt'
PHP_ROOT_MAP = '/var/www/php-roots.txt'

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

def services_config(instance_name, parser=None):
    if parser is None:
        parser = site_config(instance_name)
    services = {}
    for name in parser.options('production'):
        if name.startswith('service.'):
            services[name[len('service.'):]] = parser.get('production', name)
    return services

def load_service_module(service_name):
    __import__('tcsupport.service.%s' % service_name)
    mod = sys.modules['tcsupport.service.%s' % service_name]
    return mod


if __name__ == '__main__':
    import sys
    app_dir = sys.argv[1]
