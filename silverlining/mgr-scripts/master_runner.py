"""Called by mod_wsgi, this application finds and starts all requests

This defines application(), which is a WSGI application that mod_wsgi looks for.

It uses $SITE to figure out who to send the request to, then
configures all services, and then passes the request on to the new
application.  This loading process only happens once.

Also for each request the environment is fixed up some to represent
the request properly after having gone through Varnish.
"""
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
# Import these to work around a mod_wsgi problem:
import time, _strptime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from silversupport import common
import re
from site import addsitedir

#don't show DeprecationWarning in error.log
#TODO, make this configurable
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

found_app = None
found_app_site = None

def application(environ, start_response):
    try:
        get_app(environ)
    except:
        import traceback
        bt = traceback.format_exc()
        start_response('500 Server Error', [('Content-type', 'text/plain')])
        lines = ['There was an error loading the application:', bt, '\nEnviron:']
        for name, value in sorted(environ.items()):
            try:
                lines.append('%s=%r' % (name, value))
            except:
                lines.append('%s=<error>' % name)
        return ['\n'.join(lines)]
    return found_app(environ, start_response)

def get_app(environ):
    global found_app, found_app_site
    site = environ['SITE']
    os.environ['SITE'] = site
    os.environ['CANONICAL_HOST'] = common.canonical_hostname(site) or ''
    ## FIXME: give a real version here...
    environ['SILVER_VERSION'] = os.environ['SILVER_VERSION'] = 'silverlining/0.0'
    
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
        return found_app
    # The application group we are running:
    if not re.search(r'^[A-Za-z0-9._-]+$', site):
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

    try:
        for service, config in sorted(common.services_config(site).items()):
            common.load_service_module(service).app_setup(site, config, os.environ)
    except common.BadSite, e:
        return ErrorApp('Error loading services: %s' % e)

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
            "The setting ([production] runner) %s does not exist" % runner)

    if runner.endswith('.ini'):
        from paste.deploy import loadapp
        from silversupport.secret import get_secret
        runner = 'config:%s' % runner
        global_conf = os.environ.copy()
        global_conf['SECRET'] = get_secret()
        found_app = loadapp(runner, name=spec,
                            global_conf=global_conf)
    elif runner.endswith('.py'):
        ## FIXME: not sure what name to give it
        ns = {'__file__': runner, '__name__': 'main_py'}
        execfile(runner, ns)
        spec = spec or 'application'
        if spec in ns:
            found_app = ns[spec]
        else:
            return ErrorApp(
                "No application %s defined in %s"
                % (runner, spec))
    elif runner.startswith('static'):
        found_app = NullApplication()
    else:
        return ErrorApp(
            "Unknown kind of runner (%s)" % runner)
    found_app_site = site
    return found_app

class ErrorApp(object):
    """Application that simply displays the error message"""
    def __init__(self, message):
        self.message = message
    
    def __call__(self, environ, start_response):
        start_response('500 Error', [('Content-type', 'text/plain')])
        return [self.message]

class NullApplication(object):
    """Used with runner=null"""
    def __call__(self, environ, start_response):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found']

