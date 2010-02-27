import os
import site
import sys
site.addsitedir(os.path.abspath(os.path.join(__file__, '../../python')))
import warnings
from ConfigParser import ConfigParser

def add_tcsupport():
    toppcloud_conf = os.path.join(os.environ['HOME'], '.toppcloud.conf')
    parser = ConfigParser()
    parser.read([toppcloud_conf])
    if (not parser.has_section('environment')
        or not parser.has_option('environment', 'toppcloud_location')):
        warnings.warn('Problem loading %s: no [environment] toppcloud_location setting'
                      % toppcloud_conf)
        return
    # Now we make tcsupport importable:
    toppcloud_location = parser.get('environment', 'toppcloud_location')
    tcsupport_location = os.path.join(
        toppcloud_location, 'server-files/serverroot/var/www/support/')
    sys.path.append(tcsupport_location)

def setup_services():
    base_path = os.path.abspath(
        os.path.join(__file__, '../../../'))
    app_ini = os.path.join(base_path, 'app.ini')
    parser = ConfigParser()
    if not parser.read([app_ini]):
        warnings.warn(
            'Could not read %s' % app_ini)
        return
    app_name = parser.get('production', 'app_name')
    from tcsupport.develconfig import load_devel_config
    devel_config = load_devel_config(app_name)
    from tcsupport import common
    for service, config in sorted(common.services_config(None, parser=parser).items()):
        common.load_service_module(service).app_setup(
            app_name, config, os.environ, devel=True,
            devel_config=devel_config)

if not os.environ.get('TOPPCLOUD', '').startswith('toppcloud/'):
    # Not a production environment...
    add_tcsupport()
    setup_services()
    os.environ.setdefault('TOPPCLOUD', 'devel/0.0')

try:
    import toppcustomize
except ImportError:
    pass

