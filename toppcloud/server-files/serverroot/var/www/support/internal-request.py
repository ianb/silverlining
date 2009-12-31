#!/usr/bin/env python
import urllib
import sys
import os
from cStringIO import StringIO
from ConfigParser import ConfigParser

def make_internal_request(instance_name, hostname,
                          path, body=None, environ=None):
    basic_environ = {
        'PATH_INFO': urllib.unquote(str(path)),
        'SCRIPT_NAME': '',
        'SERVER_NAME': hostname,
        'SERVER_PORT': '80',
        'REQUEST_METHOD': 'GET',
        'HTTP_HOST': '%s:80' % hostname,
        'CONTENT_LENGTH': '0',
        'REMOTE_ADDR': '127.0.0.1',
        'wsgi.input': StringIO(''),
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
        'wsgi.url_scheme': 'http',
        'toppcloud.internal': True,
        }
    if body:
        basic_environ['wsgi.input'] = StringIO(body)
        basic_environ['CONTENT_LENGTH'] = len(body)
        basic_environ['REQUEST_METHOD'] = 'POST'
    if environ:
        basic_environ.update(environ)
    basic_environ['SITE'] = instance_name
    ns = {'__file__': 'master_runner.py',
          '__name__': '__main__'}
    execfile('/var/www/support/master_runner.py', ns)
    app = ns['application']
    out = StringIO()
    info = []
    def start_response(status, headers, exc_info=None):
        if exc_info is not None:
            raise exc_info[0], exc_info[1], exc_info[2]
        info[:] = [status, headers]
        return out.write
    app_iter = app(basic_environ, start_response)
    try:
        for item in app_iter:
            out.write(item)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
    status, headers = info
    return status, headers, out.getvalue()

def run(args=None):
    if args is None:
        args = sys.argv[1:]
    if args[0] == 'update':
        return run_update(args[1], args[2])
    instance_name = args[0]
    hostname = args[1]
    path = args[2]
    environ = {}
    body = None
    if args[3:]:
        body = args[3] or None
        for arg in args[4:]:
            name, value = arg.split('=', 1)
            environ[name] = value
    status, headers, body = make_internal_request(
        instance_name, hostname,
        path, body=body, environ=environ)
    write_output(status, headers, body)

def write_output(status, headers, body):
    sys.stdout.write('%s\n' % status)
    sys.stdout.flush()
    for name, value in headers:
        sys.stdout.write('%s: %s\n' % (name, value))
    sys.stdout.flush()
    sys.stdout.write(body)

def run_update(instance_name, hostname):
    app_ini = os.path.join('/var/www', instance_name, 'app.ini')
    parser = ConfigParser()
    parser.read([app_ini])
    if parser.has_option('production', 'update_fetch'):
        urls = parser.get('production', 'update_fetch')
        urls = [url for url in urls.splitlines()
                if url.strip() and not url.strip().startswith('#')]
        for url in urls:
            print 'Fetching update URL %s' % url
            status, headers, body = make_internal_request(
                instance_name, hostname,
                url, environ={'toppcloud.update': True})
            if not status.startswith('200'):
                sys.stdout.write(status)
                sys.stdout.flush()
            if body:
                sys.stdout.write(body)
                if not body.endswith('\n'):
                    sys.stdout.write('\n')
                sys.stdout.flush()

if __name__ == '__main__':
    run()
