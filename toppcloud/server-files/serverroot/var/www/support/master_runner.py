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
    
    # Fixup port and ipaddress
    environ['SERVER_PORT'] = '80'
    if 'HTTP_X_FORWARDED_FOR' in environ:
        environ['REMOTE_ADDR'] = environ.pop('HTTP_X_FORWARDED_FOR')
    if 'HTTP_X_VARNISH_IP' in environ:
        environ['SERVER_ADDR'] = environ.pop('HTTP_X_VARNISH_IP')
    if 'SCRIPT_URI' in environ:
        environ['SCRIPT_URI'] = environ['SCRIPT_URI'].replace(':8080', '')
    
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
    sitecustomize = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                                 'sitecustomize.py')
    if os.path.exists(sitecustomize):
        ns = {'__file__': sitecustomize, '__name__': 'sitecustomize'}
        execfile(sitecustomize, ns)

    for service, config in sorted(common.services_config(site).items()):
        common.load_service_module(service).app_setup(site, config, os.environ)

    ## FIXME: should these defaults just be deprecated?
    parser = common.site_config(site)
    if parser.has_option('production', 'runner'):
        runner = os.path.join(common.site_dir(site), parser.get('production', 'runner'))
        if '#' in runner:
            runner, spec = runner.split('#', 1)
        else:
            spec = None
    else:
        return ErrorApp(
            "app.ini did not define a runner setting")
    
    if not os.path.exists(runner):
        return ErrorApp(
            "The setting ([production] runner) %s does not exist")

    if runner.endswith('.ini'):
        from paste.deploy import loadapp
        found_app = loadapp(runner, name=spec)
    elif runner.endswith('.py'):
        ## FIXME: not sure what name to give it
        ns = {'__file__': runner, '__name__': 'main_py'}
        execfile(runner, ns)
        spec = spec or 'application'
        if spec in ns:
            found_app = ns['application']
        else:
            return ErrorApp(
                "No application %s defined in %s"
                % (runner, spec))
    found_app_site = site
    return found_app(environ, start_response)

class ErrorApp(object):
    def __init__(self, message):
        self.message = message
    
    def __call__(self, environ, start_response):
        start_response('500 Error', [('Content-type', 'text/plain')])
        return [self.message]
