#!/usr/bin/env python
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.common import services_config, load_service_module, site_config
from optparse import OptionParser

parser = OptionParser(
    usage="%prog INSTANCE_NAME",
    description="""\
Runs any setup necessary for the new instance's services.  Also
apt-get installs any packages listed in app.ini.
""")

def update_service(app_dir):
    import subprocess
    for name, config in sorted(services_config(app_dir).items()):
        mod = load_service_module(name)
        mod.install(app_dir, config)
    config = site_config(app_dir)
    if config.has_option('production', 'packages'):
        packages = config.get('production', 'packages')
        packages = [
            line.strip()
            for line in packages.splitlines()
            if line.strip() and not line.strip().startswith('#')]
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
    app_dir = args[0]
    update_service(app_dir)
