#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
import time
from silversupport import appdata
from silversupport.appconfig import AppConfig
from silversupport.util import unique_name

parser = optparse.OptionParser(
    usage='%prog LOCATION')


def main():
    options, args = parser.parse_args()
    location = args[0]
    instance_name = appdata.instance_for_location(*appdata.normalize_location(location))
    if not instance_name:
        print 'Could not match against location: %s' % location
        sys.exit(1)
    app_config = AppConfig.from_instance_name(instance_name)
    dest_dir = os.path.join('/var/lib/silverlining/backups', app_config.app_name)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    dirname = 'backup-%s-%s' % (app_config.app_name, time.strftime('%Y-%m-%d'))
    dirname = unique_name(dest_dir, dirname)
    app_config.backup_services(dirname)
    print 'backup="%s"' % dirname

if __name__ == '__main__':
    main()
