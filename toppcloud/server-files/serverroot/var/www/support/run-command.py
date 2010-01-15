#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from site import addsitedir
from tcsupport import common

def main():
    args = sys.argv[1:]
    host = args[0]
    tmp_dir = args[1]
    command = args[2]
    rest = args[3:]
    app_dir = common.app_dir_for_host(host)
    if tmp_dir and tmp_dir != 'NONE':
        rest = [
            r.replace('$TMP', tmp_dir)
            for r in rest]
    activate_dir(app_dir)
    path = os.path.join(app_dir, 'bin', command)
    ns = {'__file__': path, '__name__': '__main__'}
    os.environ['TOPPCLOUD'] = 'toppcloud/0.0'
    sys.argv = [path] + rest
    os.chdir(app_dir)
    print 'argv', sys.argv
    execfile(path, ns)

def activate_dir(base_path):
    lib_path = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                            'site-packages')
    if lib_path not in sys.path:
        addsitedir(lib_path)
    sitecustomize = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                                 'sitecustomize.py')
    if os.path.exists(sitecustomize):
        ns = {'__file__': sitecustomize, '__name__': 'sitecustomize'}
        execfile(sitecustomize, ns)

if __name__ == '__main__':
    main()
    
