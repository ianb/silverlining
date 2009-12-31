#!/usr/bin/env python
import sys, os
import optparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.common import site_dir, HOSTMAP, sites

import shutil

parser = optparse.OptionParser(
    usage='%prog [-n]')
parser.add_option(
    '-n', '--simulate',
    action='store_true',
    help="Show what would be removed, but don't remove it")

def unused_sites():
    all_sites = set(sites())
    used_sites = set()
    fp = open(HOSTMAP)
    for line in fp:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        hostname, sitename = line.split(None, 1)
        used_sites.add(sitename)
    fp.close()
    return all_sites - used_sites
   
def remove_site(site):
    print 'Removing unused site %s' % site_dir(site)
    shutil.rmtree(os.path.join(site_dir(site)))

def remove_unused_sites():
    options, args = parser.parse_args()
    simulate = options.simulate
    for site in unused_sites():
        if simulate:
            print 'Would remove site %s' % site
        else:
            remove_site(site)

if __name__ == '__main__':
    remove_unused_sites()
