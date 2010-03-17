#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import glob
import time
from silversupport.common import site_dir, sites
from optparse import OptionParser

parser = OptionParser(
    usage="%prog APP_NAME",
    description="""\
Prepares a new directory for a new instance to be uploaded.  This
creates a new unique name, creates a directory, and hardlink/copies
the directory over to be rsync'd over by the new app.  Finally it
prints the new app name for the caller to use.
""")

def prepare_new_site(site_name):
    """Creates the new directory and copies it over"""
    n = 0
    date = time.strftime('%Y-%m-%d')
    app_fn = '/var/www/%s.%s_*' % (site_name, date)
    names = list(glob.glob(app_fn))
    if not names:
        n = 1
    else:
        n = max(
            [int(name.rsplit('_', 1)[1])
             for name in names]) + 1
    app_dir = '%s.%s_%03i' % (site_name, date, n)
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
    options, args = parser.parse_args()
    site_name = args[0]
    prepare_new_site(site_name)
    
