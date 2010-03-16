#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport import common

parser = optparse.OptionParser(
    usage='%prog HOSTS')
parser.add_option(
    '--keep-prev', action='store_true',
    help='Keep the prev.* host')

def main():
    options, args = parser.parse_args()
    for host in args:
        common.remove_host(host, keep_prev=options.keep_prev)
        print 'Removed host %s' % host

if __name__ == '__main__':
    main()
    
