#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
import shutil
from silversupport import appdata

parser = optparse.OptionParser(
    usage='%prog [-n]')
parser.add_option(
    '-n', '--simulate',
    action='store_true',
    help="Show what would be removed, but don't remove it")
   
def remove_instance(instance_name):
    """Removes the instance"""
    print 'Removing unused site %s' % instance_name
    shutil.rmtree(os.path.join('/var/www', instance_name))

def remove_unused_sites():
    """Call the script; remove all unused sites"""
    options, args = parser.parse_args()
    simulate = options.simulate
    all_instances = appdata.all_app_instances()
    used = []
    for instance_name, hosts in sorted(all_instances.items()):
        if hosts:
            used.append((instance_name, hosts))
            continue
        if simulate:
            print 'Would remove instance %s' % instance_name
        else:
            remove_instance(instance_name)
    for instance_name, hostnames in used:
        hostnames = [h for h, path in hostnames
                     if ':' not in h
                     and not h.startswith('www.')]
        print 'Keeping instance %s (host: %s)' % (
            instance_name, ', '.join(sorted(hostnames)))

if __name__ == '__main__':
    remove_unused_sites()
