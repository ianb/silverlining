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
    all_sites = set(sites(True))
    all_sites -= IGNORE_SITES
    used_sites = {}
    fp = open(HOSTMAP)
    for line in fp:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        hostname, sitename = line.split(None, 1)
        used_sites.setdefault(sitename, []).append(hostname)
    fp.close()
    return used_sites, all_sites - set(used_sites)
   
def remove_site(site):
    print 'Removing unused site %s' % site_dir(site)
    shutil.rmtree(os.path.join(site_dir(site)))

def remove_unused_sites():
    options, args = parser.parse_args()
    simulate = options.simulate
    used, unused = unused_sites()
    for site in sorted(unused):
        if simulate:
            print 'Would remove site %s' % site
        else:
            remove_site(site)
    for site, hostnames in sorted(used.items()):
        hostnames = [h for h in hostnames
                     if ':' not in h
                     and not h.startswith('www.')]
        print 'Keeping site %s (host: %s)' % (
            site, ', '.join(sorted(hostnames)))

if __name__ == '__main__':
    remove_unused_sites()
