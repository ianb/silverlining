"""PHP support"""

from silversupport.shell import apt_install

import os

packages = [
    'php5',
    ]


def install(app_config, config):
    if not os.path.exists('/usr/share/doc/php5'):
        apt_install(packages)


def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    # PHP doesn't go through this setup routine
    pass
