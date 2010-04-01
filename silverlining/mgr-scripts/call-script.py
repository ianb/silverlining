import sys
import os
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runner.py')):
    # In development
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
else:
    sys.path.insert(0, '/usr/local/share/silverlining/lib')
from silversupport.appconfig import AppConfig


def main():
    instance_name = sys.argv[1]
    script = sys.argv[2]
    if instance_name.startswith('/'):
        app_ini = os.path.join(instance_name, 'app.ini')
        app_config = AppConfig(app_ini)
    else:
        app_config = AppConfig.from_instance_name(instance_name)
    app_config.activate_services(os.environ)
    app_config.activate_path()
    script = os.path.join(app_config.app_dir, script)
    ns = {'__file__': script, '__name__': '__main__'}
    sys.argv = [script] + sys.argv[3:]
    execfile(script, ns)

if __name__ == '__main__':
    main()
