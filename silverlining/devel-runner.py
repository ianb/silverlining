"""This is the server that is run for silver serve.

Note that this is a script, and is run as a script, it is not a
module.  This allows a server to be run without silverlining itself on
sys.path.
"""

# Setup sys.path to include silversupport:
from site import addsitedir
import sys
import os
from ConfigParser import ConfigParser
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)
# The parent directory ends up on sys.path, even though we don't want
# it to; here we remove it:
here = os.path.abspath(os.path.dirname(__file__))
for path in list(sys.path):
    if os.path.abspath(path) == here:
        sys.path.remove(path)
from silversupport import common
from silversupport.requests import make_internal_request
from silversupport.develconfig import load_devel_config
from silversupport.appconfig import AppConfig
import mimetypes

silverlining_conf = os.path.join(os.environ['HOME'], '.silverlining.conf')

def load_paste_reloader():
    try:
        from paste import reloader
        return reloader
    except ImportError:
        import new
        ## FIXME: not sure if this'll work well if sys.path is fixed
        ## up later with a Paste:
        init_mod = new.module('paste')
        init_mod.__path__ = []
        sys.modules['paste'] = init_mod
        mod = new.module('paste.reloader')
        init_mod.reloader = mod
        execfile(os.path.join(os.path.dirname(__file__),
                              'paste-reloader.py'),
                 mod.__dict__)
        sys.modules['paste.reloader'] = mod
        return mod

reloader = load_paste_reloader()
reloader.install()

def get_app(base_path):
    ## FIXME: is this a reasonable instance_name default?
    app_config = AppConfig(os.path.join(base_path, 'app.ini'))
    instance_name = 'localhost'
    os.environ['INSTANCE_NAME'] = instance_name
    os.environ['CANONICAL_HOST'] = 'localhost:8080'
    app_config.activate_path()
    app_name = app_config.app_name
    reloader.watch_file(app_config.config_file)
    devel_config = load_devel_config(app_name)
    app_config.activate_services(os.environ, devel=True, devel_config=devel_config)
    reloader.watch_file(app_config.runner.split('#')[0])
    found_app = app_config.get_app_from_runner()
    
    # This calls the update_fetch URL on every reload/restart, which
    # is... questionable.
    update_fetch = app_config.update_fetch
    for url in update_fetch:
        print 'Fetching update URL %s' % url
        status, headers, body = make_internal_request(
            found_app, app_name, 'localhost',
            url, environ={'silverlining.update': True})
        if not status.startswith('200'):
            sys.stdout.write(status+'\n')
            sys.stdout.flush()
        if body:
            sys.stdout.write(body)
            if not body.endswith('\n'):
                sys.stdout.write('\n')
            sys.stdout.flush()

    if app_config.writable_root_location:
        writable_root = os.environ['CONFIG_WRITABLE_ROOT']
    else:
        writable_root = None
    
    return found_app, writable_root

class CompoundApp(object):
    """Application that simulates the Apache configuration of silverlining

    This basically serves up the normal WSGI application, plus the
    static files.
    """

    def __init__(self, base_path, writable_root=None):
        self.base_path = base_path
        self.app, self.writable_root = get_app(base_path)

    def __call__(self, environ, start_response):
        environ['silverlining.devel'] = True
        path_info = environ.get('PATH_INFO', '')
        path_info = os.path.normpath(path_info)
        path_info = path_info.replace('\\', '/').lstrip('/')
        paths = [os.path.join(self.base_path, 'static', path_info)]
        if self.writable_root:
            paths.append(os.path.join(self.writable_root, path_info))
        for path in paths:
            ## FIXME: this should redirect (add / etc) same as wsgi_runner does:
            if os.path.exists(path) and os.path.isdir(path) and os.path.exists(os.path.join(path, 'index.html')):
                return self.serve_file(os.path.join(path, 'index.html'), environ, start_response)
            if os.path.exists(path) and not os.path.isdir(path):
                return self.serve_file(path, environ, start_response)
        return self.app(environ, start_response)

    def serve_file(self, path, environ, start_response):
        """Serve a file.

        This does not use any library because we want this server to
        be library-agnostic.  It's not a great server (e.g., no cache
        handling), but since this is only for development it should be
        okay.
        """
        length = os.path.getsize(path)
        type, encoding = mimetypes.guess_type(path)
        if not type:
            type = 'application/octet-stream'
        def iterator():
            fp = open(path, 'rb')
            while 1:
                chunk = fp.read(4096)
                if not chunk:
                    break
                yield chunk
            fp.close()
        start_response('200 OK', [
            ('Content-type', type),
            ('Content-length', str(length))])
        return iterator()

def main(base_path):
    app = CompoundApp(base_path)
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server(
        '127.0.0.1', 8080, app)
    print 'Serving on http://127.0.0.1:8080'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    base_path = sys.argv[1]
    main(base_path)
