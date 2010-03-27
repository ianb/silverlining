#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
from silversupport.appconfig import AppConfig
from silversupport.shell import apt_install
from optparse import OptionParser

parser = OptionParser(
    usage="%prog INSTANCE_NAME",
    description="""\
Runs any setup necessary for the new instance's services.  Also
apt-get installs any packages listed in app.ini.
""")

parser.add_option(
    '--clear',
    action='store_true',
    help='Clear the database')


def update_service(instance_name, clear=False):
    app_config = AppConfig.from_instance_name(instance_name)
    app_config.install_services(clear)
    packages = app_config.packages
    if packages:
        print 'Confirming packages installed: %s' % ', '.join(packages)
        apt_install(packages)

if __name__ == '__main__':
    options, args = parser.parse_args()
    instance_name = args[0]
    update_service(instance_name, options.clear)
