import os
import site
import sys
site.addsitedir(os.path.abspath(os.path.join(__file__, '../../python')))
import warnings
from ConfigParser import ConfigParser


def add_silversupport():
    silverlining_conf = os.path.join(os.environ['HOME'], '.silverlining.conf')
    parser = ConfigParser()
    parser.read([silverlining_conf])
    if (not parser.has_section('environment')
        or not parser.has_option('environment', 'silverlining_location')):
        warnings.warn('Problem loading %s: no [environment] silverlining_location setting'
                      % silverlining_conf)
        return
    # Now we make silversupport importable:
    silverlining_location = parser.get('environment', 'silverlining_location')
    silversupport_location = os.path.dirname(silverlining_location)
    sys.path.append(silversupport_location)

if (not os.environ.get('SILVER_VERSION', '').startswith('silverlining/')
    and not os.path.exists('/usr/local/share/silverlining/lib')):
    # Not a production environment...
    add_silversupport()
    from silversupport.appconfig import AppConfig
    app_config = AppConfig(os.path.abspath(os.path.join(__file__, '../../../app.ini')))
    app_config.activate_services(os.environ)
    os.environ.setdefault('SILVER_VERSION', 'devel/0.0')

try:
    import silvercustomize
except ImportError:
    pass
