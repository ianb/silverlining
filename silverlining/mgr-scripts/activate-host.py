#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
from silversupport import common

parser = optparse.OptionParser(
    usage='%prog HOST SITE')

def main():
    options, args = parser.parse_args()
    host = args[0]
    site = args[1]
    if site.lower() == 'prev':
        site = find_prev_site(host)
    common.update_hostmap(host, site)

def find_prev_site(hostname):
    app_dir = common.app_dir_for_host('prev.' + hostname)
    return os.path.basename(app_dir)

if __name__ == '__main__':
    main()
    
