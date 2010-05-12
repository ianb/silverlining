#!/usr/bin/env python
import sys
import os

glob_hostnames = {}
abs_hostnames = {}
filename = '/var/www/appdata.map'
mtime = 0


def loop():
    global mtime
    while 1:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            cur_mtime = os.path.getmtime(filename)
            if cur_mtime > mtime:
                mtime = cur_mtime
                read_file()
            hostname, path = line.split('^', 1)
            hostname = hostname.split(':', 1)[0]
            if not path:
                path = '/'
        except:
            import traceback
            sys.stderr.write('Odd exception in rewrite-map:\n')
            traceback.print_exc()
            sys.stdout.write('error:something odd happened\n')
            sys.stdout.flush()
            continue
        try:
            path_match, data, rest = lookup(hostname, path)
            if path_match:
                data = '%s|%s|%s' % (path_match, data, rest)
        except LookupError, e:
            sys.stderr.write('Error with hostname=%r, path=%r: %s\n'
                             % (hostname, path, e))
            sys.stderr.flush()
            data = 'error:' + str(e)
        sys.stdout.write(data.strip() + '\n')
        sys.stdout.flush()


def lookup(hostname, path):
    record = lookup_hostname(hostname)
    path_match, data, rest = lookup_path(record, path)
    return path_match, data, rest


def lookup_hostname(hostname, seen=None):
    record = None
    if hostname in abs_hostnames:
        record = abs_hostnames[hostname]
    elif glob_hostnames:
        parts = hostname.split('.')
        while parts:
            part_hostname = '.'+'.'.join(parts)
            if part_hostname in glob_hostnames:
                record = glob_hostnames[part_hostname]
            parts.pop(0)
    if record is None:
        if '*' in glob_hostnames:
            record = glob_hostnames['*']
        elif 'not-found' in abs_hostnames:
            record = abs_hostnames['not-found']
        else:
            ## FIXME: better failover?
            raise LookupError('No not-found application listed')
    if record and record[0][0] == 'seeother':
        name = record[0][1]
        if seen and name in seen:
            raise LookupError('Infinite loop of domains: %s' % seen)
        if seen is None:
            seen = [name]
        else:
            seen += [name]
        return lookup_hostname(name, seen)
    return record


def lookup_path(record, path):
    for path_prefix, data in record:
        if path == path_prefix[:-1] and path_prefix.endswith('/'):
            # We need a / redirect
            return None, 'addslash', None
        if path.startswith(path_prefix):
            path_prefix = path_prefix.rstrip('/') or '/'
            return path_prefix, data, path[len(path_prefix)-1:]
    else:
        ## FIXME: how should this fail?
        raise LookupError('No application mounted to /')


def read_file():
    fp = open(filename, 'rb')
    try:
        read_file_data(fp)
    finally:
        fp.close()


def read_file_data(fp):
    global glob_hostnames, abs_hostnames
    glob_hostnames = {}
    abs_hostnames = {}
    for line in fp:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        hostname, path, rest = line.split(None, 2)
        if hostname.startswith('.') or hostname == '*':
            glob_hostnames.setdefault(hostname, []).append((path, rest))
        else:
            abs_hostnames.setdefault(hostname, []).append((path, rest))
    for s in glob_hostnames, abs_hostnames:
        for value in s.itervalues():
            value.sort(key=lambda x: -len(x[0]))

if __name__ == '__main__':
    loop()
