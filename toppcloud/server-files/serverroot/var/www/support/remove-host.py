#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import optparse
from tcsupport import common

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
    
