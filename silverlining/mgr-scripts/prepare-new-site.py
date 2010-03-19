#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import glob
import time
from optparse import OptionParser
from silversupport import appdata

parser = OptionParser(
    usage="%prog APP_NAME",
    description="""\
Prepares a new directory for a new instance to be uploaded.  This
creates a new unique name, creates a directory, and hardlink/copies
the directory over to be rsync'd over by the new app.  Finally it
prints the new app name for the caller to use.
""")


def prepare_new_site(app_name):
    """Creates the new directory and copies it over"""
    n = 0
    date = time.strftime('%Y-%m-%d')
    app_dirs = '/var/www/%s.%s_*' % (app_name, date)
    names = list(glob.glob(app_dirs))
    if not names:
        n = 1
    else:
        n = max(
            [int(name.rsplit('_', 1)[1])
             for name in names]) + 1
    app_dir = '%s.%s_%03i' % (app_name, date, n)
    other_instances = []
    print appdata.list_instances()
    for instance_name in appdata.list_instances():
        if instance_name.startswith('%s.' % app_name):
            other_instances.append(instance_name)
    if other_instances:
        copy_instance = sorted(other_instances)[-1]
        hardlink_copy(os.path.join('/var/www', copy_instance), app_dir)
    else:
        os.mkdir(os.path.join('/var/www', app_dir))
    print 'instance_name="%s"' % app_dir


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
    app_name = args[0]
    prepare_new_site(app_name)
