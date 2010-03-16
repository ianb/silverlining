#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
from silversupport import common
import glob
from ConfigParser import ConfigParser

parser = optparse.OptionParser(
    usage='%prog HOST SITE')

def main():
    options, args = parser.parse_args()
    host = args[0]
    site = args[1]
    if site.isdigit():
        # Then it's a version
        site = find_site_by_version(site, host)
    elif site.lower() == 'prev':
        site = find_prev_site(host)
    common.update_hostmap(host, site)
    if (not host.split('.')[0].isdigit()
        and site.lower() not in ('disabled', 'notfound')):
        # Also set the version:
        p = ConfigParser()
        p.read([os.path.join(common.site_dir(site), 'app.ini')])
        version = p.get('production', 'version')
        common.update_hostmap('%s.%s' % (version, host), site)

def find_site_by_version(version, hostname):
    app_dir = common.app_dir_for_host(hostname)
    site_name = os.path.basename(app_dir).split('.')[0]
    names = glob.glob('/var/www/%s.*' % site_name)
    names = [os.path.basename(name).split('.') for name in names]
    names = sorted([spec for spec in names
             if spec[1] == version],
                   key=lambda spec: (spec[1], int(spec[2].rsplit('_')[1])))
    most_recent = '.'.join(names[-1])
    return most_recent

def find_prev_site(hostname):
    app_dir = common.app_dir_for_host('prev.' + hostname)
    return os.path.basename(app_dir)

if __name__ == '__main__':
    main()
    
