import os
import sys
import re
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

def app_dir_for_host(hostname):
    fp = open(HOSTMAP)
    try:
        for line in fp:
            h, instance_name = line.strip().split(None, 1)
            if h == hostname:
                return os.path.join('/var/www', instance_name)
        raise LookupError(
            "No app with the hostname %s" % hostname)
    finally:
        fp.close()

def update_hostmap(hostname, appname):
    """Updates /var/www/hostmap.txt with the new hostname to appname
    association

    This is called multiple times to update the hostmap.  It also
    creates the prev.hostname association (pointing to the old app).
    """
    fp = open(HOSTMAP)
    lines = list(fp)
    fp.close()
    hostnames = [
      hostname,
      hostname+':80',
      hostname+':443',
      'www.'+hostname,
      'www.'+hostname+':80',
      'www.'+hostname+':443',
    ]
    new_lines = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        line_hostname, line_appname = line.strip().split(None, 1)
        if line_hostname in hostnames:
            new_lines.append('prev.%s %s\n' % (line_hostname, line_appname))
            #print 'Renaming host %s to prev.%s' % (line_hostname, line_hostname)
            continue
        if (line_hostname.startswith('prev.')
            and line_hostname[5:] in hostnames):
            #print 'Removing line %s' % line.strip()
            continue
        new_lines.append(line)
    for hostname in hostnames:
        new_lines.append('%s %s\n' % (hostname, appname))
    ## FIXME: This should just append to the file when that's possible:
    fp = open(HOSTMAP, 'w')
    fp.writelines(new_lines)
    fp.close()

def remove_host(hostname, keep_prev):
    """Updates /var/www/hostmap.txt to remove the given hostname"""
    if not keep_prev:
        prev = r'(?:prev\.)?'
    hostname_re = re.compile(
        r'^%s(?:www\.)?(?:\d+\.)?%s(?::80)?(?::443)?$' %
        (prev, re.escape(hostname)),
        re.I)
    fp = open(HOSTMAP)
    lines = list(fp)
    fp.close()
    new_lines = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        line_hostname, line_appname = line.strip().split(None, 1)
        if not hostname_re.search(line_hostname):
            new_lines.append(line)
    fp = open(HOSTMAP, 'w')
    fp.writelines(new_lines)
    fp.close()

if __name__ == '__main__':
    app_dir = sys.argv[1]
