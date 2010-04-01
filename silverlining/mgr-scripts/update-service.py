#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from optparse import OptionParser
from silversupport.appconfig import AppConfig
from silversupport.appdata import instance_for_location, normalize_location
from silversupport.shell import apt_install, run

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

parser.add_option(
    '--location',
    help='location to update/clear (instead of INSTANCE_NAME)')

php_packages = [
    'php5',
    'php5-cgi',
    'php5-cli',
    'libapache2-mod-php5',
    ]


def update_service(instance_name, clear=False):
    app_config = AppConfig.from_instance_name(instance_name)
    app_config.install_services(clear)
    packages = app_config.packages
    if packages:
        print 'Confirming packages installed: %s' % ', '.join(packages)
        apt_install(packages)
    if (app_config.platform == 'php' and
        (not os.path.exists('/usr/share/doc/php5')
         or not os.path.exists('/usr/bin/php5'))):
        apt_install(packages)
        run(['a2enmod', 'php5'])
        run(['/etc/init.d/apache2', 'restart'])


if __name__ == '__main__':
    options, args = parser.parse_args()
    if options.location:
        instance_name = instance_for_location(*normalize_location(options.location))
    else:
        instance_name = args[0]
    update_service(instance_name, options.clear)
