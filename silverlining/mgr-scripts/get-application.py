#!/usr/bin/env python
"""Find the application for a location"""

import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
from silversupport import appdata


def main():
    hostname, path = appdata.normalize_location(sys.argv[1])
    instance = appdata.instance_for_location(hostname, path)
    appname = instance.split('.')[0]
    print appname
    return 0

if __name__ == '__main__':
    sys.exit(main())
