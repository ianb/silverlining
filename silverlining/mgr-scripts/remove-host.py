#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport import appdata

parser = optparse.OptionParser(
    usage='%prog HOSTS')
parser.add_option(
    '--keep-prev', action='store_true',
    help='Keep the prev.* host')


def main():
    options, args = parser.parse_args()
    locations = [appdata.normalize_location(l, empty_path=None) for l in args]
    for hostname, path in locations:
        removed = appdata.remove_host(hostname, path=path, keep_prev=options.keep_prev)
        if not removed:
            print 'No entries found matching %s' % (hostname + (path or ''))
        elif len(removed) == 1:
            print 'Removed %s: %s' % (hostname + (path or ''), removed[0].strip())
        else:
            print 'Removed %s:' % (hostname + (path or ''))
            for line in removed:
                print '  %s' % line.strip()

if __name__ == '__main__':
    main()
