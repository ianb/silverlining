#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import optparse
import shutil
from silversupport import transfermethods

parser = optparse.OptionParser(
    usage='%prog DIR DEST')
parser.add_option(
    '--remove', action='store_true',
    help="Remove the DIR after successful transfer")
parser.add_option(
    '--archive', action='store_true',
    help="Create an archive and print the result, instead of transfering")


def main():
    options, args = parser.parse_args()
    dir = args[0]
    dest = args[1]
    if options.archive:
        run_archive(dir, dest)
        return
    if dest.startswith('remote:'):
        dest = dest[len('remote:'):]
        dest = os.path.join('/var/lib/silverlining/backups', dest)
        transfermethods.local(dir, dest)
    elif dest.startswith('site:'):
        raise NotImplementedError('site: has not yet been implemented')
    elif dest.startswith('ssh:'):
        dest = dest[len('ssh:'):].lstrip('/')
        if '/' in dest:
            hostname, path = dest.split('/', 1)
            if path.lower().startswith('cwd/'):
                path = path[4:]
            else:
                path = '/' + path
        else:
            hostname = dest
            path = ''
        transfermethods.ssh(dir, '%s:%s' % (hostname, path))
    elif dest.startswith('rsync:'):
        dest = dest[len('rsync:'):]
        transfermethods.rsync(dir, dest)
    else:
        print 'Unknown destination type: %s' % dest
        sys.exit(1)
    if options.remove:
        shutil.rmtree(dir)


def run_archive(dir, ext):
    tmp = transfermethods.make_temp_name('file'+ext)
    transfermethods.archive(dir, tmp)
    print 'archive="%s"' % tmp

if __name__ == '__main__':
    main()
