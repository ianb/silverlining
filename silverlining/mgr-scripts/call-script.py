import sys
import os
if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runner.py')):
    # In development
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
else:
    sys.path.insert(0, '/usr/local/share/silverlining/lib')
import optparse
from silversupport.appconfig import AppConfig

parser = optparse.OptionParser(
    usage='%prog INSTANCE_NAME_OR_DIR SCRIPT')


def main():
    options, args = parser.parse_args()
    instance_name = args[0]
    script = args[1]
    if instance_name.startswith('/'):
        app_ini = os.path.join(instance_name, 'app.ini')
        app_config = AppConfig(app_ini)
    else:
        app_config = AppConfig.from_instance_name(instance_name)
    app_config.activate_path()
    app_config.activate_services(os.environ)
    script = os.path.join(app_config.app_dir, script)
    ns = {'__file__': script, '__name__': '__main__'}
    execfile(script, ns)

if __name__ == '__main__':
    main()
