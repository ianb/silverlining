#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from silversupport import appdata
from silversupport.appconfig import AppConfig

def main():
    args = sys.argv[1:]
    hostname, path = appdata.normalize_locations([args[0]])[0]
    tmp_dir = args[1]
    command = args[2]
    rest = args[3:]
    instance_name = appdata.instance_for_location(hostname, path)
    if not instance_name:
        print 'No instance found attached to %s%s' % (hostname, path)
        return 1
    app_config = AppConfig.from_appinstance(instance_name)
    
    if tmp_dir and tmp_dir != 'NONE':
        rest = [
            r.replace('$TMP', tmp_dir)
            for r in rest]
    path = os.path.join(app_config.app_dir, 'bin', command)
    os.environ['SILVER_VERSION'] = 'silverlining/0.0'
    app_config.activate_path()
    app_config.activate_services()
    # Buffering can happen because this isn't obviously hooked up to a
    # terminal (even though it is indirectly):
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.argv = [path] + rest
    os.chdir(app_config.app_dir)
    ns = {'__file__': path, '__name__': '__main__'}
    execfile(path, ns)

if __name__ == '__main__':
    sys.exit(main())
    
