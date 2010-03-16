#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
import zipfile
import warnings
from cStringIO import StringIO

parser = optparse.OptionParser(
    usage="%prog < zip")

def main():
    options, args = parser.parse_args()
    with warnings.catch_warnings():
        # I don't care if it is theoretically insecure
        warnings.simplefilter("ignore")
        location = os.tempnam(None, 'save-tmp-files-')
    os.mkdir(location)
    input = StringIO(sys.stdin.read())
    zip = zipfile.ZipFile(input, 'r')
    zip.extractall(location)
    zip.close()
    print 'tmp="%s"' % location

if __name__ == '__main__':
    main()
    
