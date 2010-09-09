#!/usr/bin/env python

import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport import disabledapps
from silversupport import appdata

parser = optparse.OptionParser(
    usage='%prog application')

parser.add_option(
    '--enable',
    action='store_true',
    help='renable a previously disabled application')


def main():
    options, args = parser.parse_args()
    application, = args
    in_use = any(True for instance, uses in appdata.all_app_instances().items()
                 if instance.startswith(application + '.') and uses)
    if not in_use:
        sys.stderr.write("%s is not in use in appdata.map\n" % application)
        return 1
    if options.enable:
        if not disabledapps.is_disabled(application):
            sys.stderr.write("%s is not disabled\n" % application)
            return 1
        disabledapps.enable_application(application)
    else:
        if disabledapps.is_disabled(application):
            sys.stderr.write("%s is already disabled\n" % application)
            return 1
        disabledapps.disable_application(application)
    return 0

if __name__ == '__main__':
    sys.exit(main())
