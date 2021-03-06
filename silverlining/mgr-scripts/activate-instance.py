#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport import appdata

parser = optparse.OptionParser(
    usage='%prog HOST SITE')

parser.add_option(
    '--debug-single-process',
    action='store_true',
    help='Set the activated application to be debug/threaded/single-process')


def main():
    options, args = parser.parse_args()
    hostname, path = appdata.normalize_location(args[0])
    instance_name = args[1]
    if instance_name.lower() == 'prev':
        instance_name = appdata.instance_for_location('prev.'+hostname, path)
        if instance_name is None:
            print 'There is no host at prev.%s%s to activate/revert' % (hostname, path)
            return 1
    appdata.add_appdata(
        instance_name, [(hostname, path)],
        debug_single_process=options.debug_single_process)
    print '%s%s mapped to instance %s' % (hostname, path, instance_name)

if __name__ == '__main__':
    sys.exit(main())
