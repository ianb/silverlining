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
# Import these to work around a mod_wsgi problem:
import time, _strptime
import os
import re
import urllib
import threading
from silversupport.appconfig import AppConfig

#don't show DeprecationWarning in error.log
#TODO, make this configurable
import warnings
warnings.simplefilter('ignore', DeprecationWarning)

found_app = None
found_app_instance_name = None
error_collector = None


def application(environ, start_response):
    try:
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
        try:
            return found_app(environ, start_response)
        except:
            import traceback
            traceback.print_exc()
            raise
    finally:
        if error_collector is not None:
            error_collector.flush_request(environ)


def get_app(environ):
    global found_app, found_app_instance_name, error_collector
    delete_boring_vars(environ)
    instance_name = environ['SILVER_INSTANCE_NAME']
    os.environ['SILVER_INSTANCE_NAME'] = instance_name
    app_config = AppConfig.from_instance_name(instance_name)
    if error_collector is None:
        log_location = os.path.join('/var/log/silverlining/apps', app_config.app_name)
        if not os.path.exists(log_location):
            os.makedirs(log_location)
        error_collector = ErrorCollector(os.path.join(log_location, 'errors.log'))
        sys.stderr = sys.stdout = error_collector
    error_collector.start_request()
    environ['silverlining.apache_errors'] = environ['wsgi.errors']
    environ['wsgi.errors'] = error_collector
    os.environ['SILVER_CANONICAL_HOSTNAME'] = app_config.canonical_hostname()
    ## FIXME: give a real version here...
    environ['SILVER_VERSION'] = os.environ['SILVER_VERSION'] = 'silverlining/0.0'
    if 'SILVER_MATCH_PATH' in environ:
        path = urllib.unquote(environ.pop('SILVER_MATCH_PATH'))
        if path != '/':
            # Only paths besides / are interesting
            environ['SCRIPT_NAME'] += path
            assert environ['PATH_INFO'].startswith(path)
            environ['PATH_INFO'] = environ['PATH_INFO'][len(path):]
            assert not environ['PATH_INFO'] or environ['PATH_INFO'].startswith('/'), (
                "Bad PATH_INFO: %r (SCRIPT_NAME: %r, SILVER_MATCH_PATH: %r)" %
                (environ['PATH_INFO'], environ['SCRIPT_NAME'], path))

    # Fixup port and ipaddress
    environ['SERVER_PORT'] = '80'
    if 'HTTP_X_FORWARDED_FOR' in environ:
        environ['REMOTE_ADDR'] = environ.pop('HTTP_X_FORWARDED_FOR', '').split(',')[0]
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

    app_config.activate_services(os.environ)
    app_config.activate_path()

    try:
        found_app = app_config.get_app_from_runner()
    except Exception, e:
        raise
        return ErrorApp(
            "Could not load the runner %s: %s" % (app_config.runner, e))
    assert found_app is not None, (
        "app_config %r.get_app_from_runner() returned None")
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
    'SILVER_PHP_ROOT', 'SILVER_REDIR_HOST', 'SILVER_FORWARDED',
    'SILVER_HOST', 'SILVER_REMAINING_URI']


def delete_boring_vars(environ):
    for name in BORING_VARS:
        if name in environ:
            del environ[name]


class ErrorCollector(object):
    def __init__(self, filename):
        self.filename = filename
        self.buffers = threading.local()

    def start_request(self):
        self.buffers.start_time = time.time()
        self.buffers.buffer = []

    def write(self, text):
        if isinstance(text, unicode):
            text = text.encode('utf8')
        self.buffers.buffer.append(text)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def flush(self):
        ## FIXME: should this do something?
        pass

    def close(self):
        ## FIXME: should this exist?
        pass

    def flush_request(self, environ):
        if not self.buffers.buffer:
            return
        total = time.time() - self.buffers.start_time
        buf = self.buffers.buffer
        date_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.buffers.start_time))
        req_name = (
            environ['REQUEST_METHOD'] + ' ' +
            environ.get('SCRIPT_NAME', '') +
            environ.get('PATH_INFO', ''))
        buf.insert(0, 'Errors for request %s (%s, %fsec):\n'
                   % (req_name, date_formatted, total))
        if not buf[-1].endswith('\n'):
            buf.append('\n')
        buf.append('Finish errors for request %s (%s)\n' % (req_name, date_formatted))
        complete = ''.join(buf)
        fp = open(self.filename, 'a')
        fp.write(complete)
        fp.flush()
        fp.close()
        self.buffers.buffer[:] = []

    def __repr__(self):
        return '<silverlining error collector %s>' % self.filename
