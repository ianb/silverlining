#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.common import HOSTMAP, PLATFORM_MAP, PHP_ROOT_MAP
from ConfigParser import ConfigParser

import sys

def update_hostmap(hostname, appname):
    fp = open(HOSTMAP)
    lines = list(fp)
    fp.close()
    hostnames = [
      hostname,
      hostname+':80',
      hostname+':443',
      'www.'+hostname,
      'www.'+hostname+':80',
      'www.'+hostname+':443',
    ]
    new_lines = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        line_hostname, line_appname = line.strip().split(None, 1)
        if line_hostname in hostnames:
            new_lines.append('prev.%s %s\n' % (line_hostname, line_appname))
            #print 'Renaming host %s to prev.%s' % (line_hostname, line_hostname)
            continue
        if (line_hostname.startswith('prev.')
            and line_hostname[5:] in hostnames):
            #print 'Removing line %s' % line.strip()
            continue
        new_lines.append(line)
    for hostname in hostnames:
        new_lines.append('%s %s\n' % (hostname, appname))
    ## FIXME: This should just append to the file when that's possible:
    fp = open(HOSTMAP, 'w')
    fp.writelines(new_lines)
    fp.close()

def set_platforms(appname):
    parser = ConfigParser()
    if not parser.read([os.path.join('/var/www', appname, 'app.ini')]):
        raise Exception('Could not find app.ini')
    if parser.has_option('production', 'service.php'):
        print 'Setting %s as a php service' % appname
        fp = open(PLATFORM_MAP, 'a')
        fp.write('%s php\n' % appname)
        fp.close()
        if parser.has_option('production', 'php_root'):
            fp = open(PHP_ROOT_MAP, 'a')
            fp.write('%s %s\n' % (appname, parser.get('production', 'php_root')))
            fp.close()

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    appname = args[0]
    for hostname in args[1:]:
        ## FIXME: for multiple hostnames, it shouldn't rewrite the hostmap.txt
        ## each time.
        update_hostmap(hostname, appname)
    set_platforms(appname)
    
