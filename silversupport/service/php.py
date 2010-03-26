"""PHP support"""

from silversupport.shell import apt_install, run

import os

packages = [
    'php5',
    'libapache2-mod-php5',
    ]


def install(app_config, config):
    if not os.path.exists('/usr/share/doc/php5'):
        apt_install(packages)
        run(['a2enmod', 'php5'])
        run(['/etc/init.d/apache2', 'restart'])


def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    # PHP doesn't go through this setup routine
    pass
