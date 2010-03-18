"""Called by mod_wsgi, this application finds and starts all requests

This defines application(), which is a WSGI application that mod_wsgi looks for.

It uses $SILVER_INSTANCE_NAME to figure out who to send the request to, then
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
from silversupport.appconfig import AppConfig
import re

#don't show DeprecationWarning in error.log
#TODO, make this configurable
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

found_app = None
found_app_instance_name = None

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
    global found_app, found_app_instance_name
    delete_boring_vars(environ)
    instance_name = environ['SILVER_INSTANCE_NAME']
    os.environ['SILVER_INSTANCE_NAME'] = instance_name
    app_config = AppConfig.from_appinstance(instance_name)
    os.environ['SILVER_CANONICAL_HOST'] = app_config.canonical_hostname()
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
        assert found_app_instance_name == instance_name, (
            "second request with unexpected instance_name (first request had instance_name=%r; "
            "next request had instance_name=%r)" % (found_app_instance_name, instance_name))
        return found_app
    # The application group we are running:
    if not re.search(r'^[A-Za-z0-9._-]+$', instance_name):
        raise Exception("Bad instance_name: %r" % instance_name)

    site_dir = app_config.app_dir
    app_config.activate_path()

    try:
        app_config.activate_services(os.environ)
    except common.BadSite, e:
        return ErrorApp('Error loading services: %s' % e)

    try:
        found_app = app_config.get_app_from_runner()
    except Exception, e:
        return ErrorApp(
            "Could not load the runner %s: %s" % (app_config.runner, e))
    found_app_instance_name = instance_name
    return found_app

class ErrorApp(object):
    """Application that simply displays the error message"""
    def __init__(self, message):
        self.message = message
    
    def __call__(self, environ, start_response):
        start_response('500 Server Error', [('Content-type', 'text/plain')])
        return [self.message]

# These are variables set in Apache/wsgi_runner, that are often quite
# dull but used internally; we'll delete them for cleanliness:
BORING_VARS = [
    'SILVER_APP_DATA', 'SILVER_PROCESS_GROUP', 'SILVER_PLATFORM',
    'SILVER_PHP_ROOT']

def delete_boring_vars(environ):
    for name in BORING_VARS:
        if name in environ:
            del environ[name]

