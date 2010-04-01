#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
import shutil
from silversupport.appconfig import AppConfig
from silversupport import transfermethods

parser = optparse.OptionParser(
    usage='%prog LOCAL_BACKUP LOCATION')
parser.add_option(
    '--keep', action='store_true',
    help="Keep the archive after restoring")


def main():
    options, args = parser.parse_args()
    local_backup = args[0]
    location = args[1]
    app_config = AppConfig.from_location(location)
    if transfermethods.is_archive(local_backup):
        dir = transfermethods.make_temp_name()
        transfermethods.unarchive(local_backup, dir)
        if not options.keep:
            os.unlink(local_backup)
            options.keep = False
        local_backup = dir
    app_config.restore_services(local_backup)
    if not options.keep:
        shutil.rmtree(local_backup)

if __name__ == '__main__':
    main()
