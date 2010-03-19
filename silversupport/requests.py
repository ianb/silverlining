"""For running internal requests in production"""

from cStringIO import StringIO
import os
import sys
import urllib

__all__ = ['make_internal_request', 'create_wsgi_app']


def make_internal_request(wsgi_app, instance_name, hostname,
                          path, body=None, environ=None):
    """Make an internal request:

    ``wsgi_app``: The application to request from (use
    ``create_wsgi_app`` to get this)

    ``instance_name``: name of the application

    ``hostname``: the hostname to request agains

    ``path``: the request path

    ``body``: any request body

    ``environ``: any extra WSGI environment you want to add

    This makes an entirely internal request.  appdata.map does not
    need to be updated to run this command, you can run it on an old
    app or an application that has not been entirely deployed.

    This returns ``(status, header_list, body_as_str)``
    """
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
        'silverlining.internal': True,
        }
    if body:
        basic_environ['wsgi.input'] = StringIO(body)
        basic_environ['CONTENT_LENGTH'] = len(body)
        basic_environ['REQUEST_METHOD'] = 'POST'
    if environ:
        basic_environ.update(environ)
    basic_environ['SILVER_INSTANCE_NAME'] = instance_name
    out = StringIO()
    info = []

    def start_response(status, headers, exc_info=None):
        if exc_info is not None:
            raise exc_info[0], exc_info[1], exc_info[2]
        info[:] = [status, headers]
        return out.write
    app_iter = wsgi_app(basic_environ, start_response)
    try:
        for item in app_iter:
            out.write(item)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
    status, headers = info
    return status, headers, out.getvalue()


def create_wsgi_app(instance_name):
    os.environ['SITE'] = instance_name
    fn = '/usr/local/share/silverlining/mgr-scripts/master_runner.py'
    ns = {'__file__': fn,
          '__name__': '__main__'}
    execfile(fn, ns)
    wsgi_app = ns['application']
    return wsgi_app
