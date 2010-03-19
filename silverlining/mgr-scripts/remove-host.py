#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport import appdata
import fnmatch
import re

parser = optparse.OptionParser(
    usage='%prog HOSTS')
parser.add_option(
    '--keep-prev', action='store_true',
    help='Keep the prev.* host')


def main():
    options, args = parser.parse_args()
    locations = []
    existing = appdata.all_app_instances()
    for location in args:
        hostname, path = appdata.normalize_location(location, empty_path=None)
        if '*' in location:
            hostname_match = re.compile(fnmatch.translate(hostname), re.I)
            if path is not None:
                path_match = re.compile(fnmatch.translate(path))
            else:
                path_match = None
            for instance_name, ex_location in existing.iteritems():
                for ex_hostname, ex_path in ex_location:
                    if ((ex_hostname == 'disabled' and hostname != 'disabled')
                        or (ex_hostname == 'not-found' and hostname != 'not-found')):
                        # Only allow explicit disabling of these hosts
                        continue
                    if (hostname_match.match(ex_hostname)
                        and (path_match is None or path_match.search(ex_path))):
                        locations.append((ex_hostname, ex_path))
        else:
            locations.append((hostname, path))

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
