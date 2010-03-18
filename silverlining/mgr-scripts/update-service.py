#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from silversupport.appconfig import AppConfig
from optparse import OptionParser

parser = OptionParser(
    usage="%prog INSTANCE_NAME",
    description="""\
Runs any setup necessary for the new instance's services.  Also
apt-get installs any packages listed in app.ini.
""")

def update_service(instance_name):
    import subprocess
    app_config = AppConfig.from_appinstance(instance_name)
    app_config.install_services()
    packages = app_config.packages
    if packages:
        print 'Confirming packages installed: %s' % ', '.join(packages)
        env = os.environ.copy()
        env['LANG'] = 'C'
        proc = subprocess.Popen(
            ['apt-get', '-y', '-q', 'install'] + packages,
            env=env)
        proc.communicate()

if __name__ == '__main__':
    options, args = parser.parse_args()
    instance_name = args[0]
    update_service(instance_name)
