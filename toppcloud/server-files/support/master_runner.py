import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport import common
import re
from site import addsitedir

found_app = None
found_app_site = None

def application(environ, start_response):
    global found_app, found_app_site
    site = environ['SITE']
    os.environ['SITE'] = site
    if found_app:
        assert found_app_site == site, (
            "second request with unexpected site (first request had site=%r; "
            "next request had site=%r)" % (found_app_site, site))
        return found_app(environ, start_response)
    # The application group we are running:
    if not re.search(r'^[a-z0-9._-]+$', site):
        raise Exception("Bad site: %r" % site)

    base_path = common.site_dir(site)

    lib_path = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                            'site-packages')
    if lib_path not in sys.path:
        addsitedir(lib_path)

    for service, config in sorted(common.services_config(site).items()):
        common.load_service_module(service).app_setup(site, config, os.environ)

    config_ini = os.path.join(base_path, 'config.ini')
    main_py = os.path.join(base_path, 'main.py')
    if os.path.exists(config_ini):
        from paste.deploy import loadapp
        found_app = loadapp(config_ini)
    elif os.path.exists(main_py):
        ## FIXME: not sure what name to give it
        ns = {'__file__': main_py, '__name__': 'main_py'}
        execfile(main_py, ns)
        if 'application' in ns:
            found_app = ns['application']
        else:
            raise NameError('No application() defined in %s' % main_py)
    else:
        raise OSError("No config.ini or main.py in %s" % base_path)
    found_app_site = site
    return found_app(environ, start_response)

