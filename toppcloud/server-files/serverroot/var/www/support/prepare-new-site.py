#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.common import site_dir, sites

import time
import os

def prepare_new_site(site_name, version):
    n = 0
    date = time.strftime('%Y-%m-%d')
    app_dir = '%s.%s.%s' % (site_name, version, date)
    while os.path.exists(site_dir(app_dir)):
        n += 1
        app_dir = '%s.%s.%s_%s' % (site_name, version, date, n)
    other_sites = []
    for name in sites():
        if name.startswith('%s.' % site_name):
            other_sites.append(name)
    if other_sites:
        copy_site = sorted(other_sites)[-1]
        hardlink_copy(site_dir(copy_site), site_dir(app_dir))
    else:
        os.mkdir(site_dir(app_dir))
    print 'app_dir="%s"' % app_dir

def hardlink_copy(source, dest):
    """Copies over a tree, using hard links"""
    for dirpath, dirnames, filenames in os.walk(source):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            assert path.startswith(source)
            new_path = path[len(source):].lstrip('/')
            new_path = os.path.join(dest, new_path)
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            os.link(path, new_path)

if __name__ == '__main__':
    import sys
    site_name = sys.argv[1]
    version = sys.argv[2]
    prepare_new_site(site_name, version)
    