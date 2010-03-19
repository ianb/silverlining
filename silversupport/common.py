import os
import sys

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

if __name__ == '__main__':
    app_dir = sys.argv[1]
