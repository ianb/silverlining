import os
import subprocess

packages = [
    'php5',
    ]

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'

    if not os.path.exists('/usr/share/doc/php5'):
        proc = subprocess.Popen(
            ['apt-get', '-y', 'install'] + packages,
            env=env)
        proc.communicate()

def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    # PHP doesn't go through this setup routine
    pass
