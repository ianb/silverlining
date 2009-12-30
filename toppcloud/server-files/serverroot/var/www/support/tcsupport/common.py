import os
import sys
from ConfigParser import ConfigParser

SITE_DIR = '/var/www'
HOSTMAP = '/var/www/hostmap.txt'

def sites():
    sites = []
    for name in os.listdir(SITE_DIR):
        if (name != 'support' 
            and os.path.isdir(os.path.join(SITE_DIR, name))):
            sites.append(name)
    return sites

def site_dir(site_name):
    return os.path.join(SITE_DIR, site_name)

def services_config(app_dir):
    app_ini = os.path.join(site_dir(app_dir), 'app.ini')
    if not os.path.exists(app_ini):
        return {}
    
    parser = ConfigParser()
    parser.read([app_ini])
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
