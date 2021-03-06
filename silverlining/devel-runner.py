"""This is the server that is run for silver serve.

Note that this is a script, and is run as a script, it is not a
module.  This allows a server to be run without silverlining itself on
sys.path.
"""

# Setup sys.path to include silversupport:
import sys
import os
path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)
# The parent directory ends up on sys.path, even though we don't want
# it to; here we remove it:
here = os.path.abspath(os.path.dirname(__file__))
for path in list(sys.path):
    if os.path.abspath(path) == here:
        sys.path.remove(path)
import shlex
import mimetypes
from silversupport.requests import internal_request
from silversupport.appconfig import AppConfig
from silversupport.shell import run

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

def load_paste_httpserver():
    try:
        from paste import httpserver
        return httpserver
    except ImportError:
        pass
    import new
    import sys
    fn = os.environ['SILVER_PASTE_LOCATION']
    if fn.endswith('.pyc'):
        fn = fn[:-1]
    util_init = os.path.join(os.path.dirname(fn), 'util', '__init__.py')
    mod = new.module('paste.util')
    mod.__file__ = util_init
    execfile(mod.__file__, mod.__dict__)
    mod.__path__ = os.path.dirname(util_init)
    sys.modules['paste.util'] = mod
    util_converters = os.path.join(os.path.dirname(fn), 'util', 'converters.py')
    cmod = new.module('paste.util.converters')
    cmod.__file__ = util_converters
    execfile(cmod.__file__, cmod.__dict__)
    sys.modules['paste.util.converters'] = cmod
    mod.converters = cmod
    mod = new.module('paste.httpserver')
    mod.__file__ = fn
    execfile(mod.__file__, mod.__dict__)
    return mod


def get_app(base_path):
    ## FIXME: is this a reasonable instance_name default?
    app_config = AppConfig(
        os.path.join(base_path, 'app.ini'),
        local_config=os.environ.get('SILVER_APP_CONFIG') or None)
    instance_name = 'localhost'
    os.environ['SILVER_INSTANCE_NAME'] = instance_name
    os.environ['SILVER_CANONICAL_HOSTNAME'] = 'localhost'
    app_config.activate_services(os.environ)
    app_config.activate_path()
    reloader.watch_file(app_config.config_file)
    reloader.watch_file(app_config.runner.split('#')[0])
    found_app = app_config.get_app_from_runner()

    # This calls the update_fetch URL on every reload/restart, which
    # is... questionable.
    update_fetch = app_config.update_fetch
    for url in update_fetch:
        if url.startswith('script:'):
            script = url[len('script:'):]
            print 'Running update script %s' % script
            call_script(app_config, script)
        else:
            print 'Fetching update URL %s' % url
            status, headers, body = internal_request(
                app_config, 'localhost',
                url, environ={'silverlining.update': True})
            if not status.startswith('200'):
                sys.stdout.write(status + '\n')
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


def call_script(app_config, script):
    run([sys.executable, os.path.join(os.path.dirname(__file__), 'mgr-scripts', 'call-script.py'),
         app_config.app_dir] + shlex.split(script))


class CompoundApp(object):
    """Application that simulates the Apache configuration of silverlining

    This basically serves up the normal WSGI application, plus the
    static files.
    """

    def __init__(self, base_path, writable_root=None):
        self.base_path = base_path
        self._app = self.writable_root = None
        self.app

    @property
    def app(self):
        if self._app is not None:
            return self._app
        prev_modules = sys.modules.keys()
        try:
            self._app, self.writable_root = get_app(self.base_path)
            return self._app
        except:
            self._app = None
            # Make sure any stale/SyntaxError modules are removed:
            for mod_name in sys.modules.keys():
                if mod_name not in prev_modules:
                    del sys.modules[mod_name]
            return self.make_error_app()

    def make_error_app(self):
        import traceback
        exc_info = sys.exc_info()
        error = ''.join(traceback.format_exception(*exc_info))
        print >> sys.stderr, error

        def app(environ, start_response):
            start_response('500 Server Error',
                           [('content-type', 'text/plain')])
            return ['Error loading app:\n', error]
        app.is_error = True
        return app

    def __call__(self, environ, start_response):
        app = self.app
        if getattr(app, 'is_error', False):
            return app(environ, start_response)
        environ['silverlining.devel'] = True
        path_info = environ.get('PATH_INFO', '')
        path_info = os.path.normpath(path_info)
        path_info = path_info.replace('\\', '/').lstrip('/')
        paths = [os.path.join(self.base_path, 'static', path_info)]
        if self.writable_root:
            paths.append(os.path.join(self.writable_root, path_info))
        for path in paths:
            if os.path.exists(path) and os.path.isdir(path) and os.path.exists(os.path.join(path, 'index.html')):
                if not environ['PATH_INFO'].endswith('/'):
                    start_response(
                        '301 Moved Permanently',
                        [('Location', environ.get('SCRIPT_NAME', '') + environ['PATH_INFO'] + '/')])
                    return ['']
                return self.serve_file(os.path.join(path, 'index.html'), environ, start_response)
            if os.path.exists(path) and not os.path.isdir(path):
                return self.serve_file(path, environ, start_response)
        return app(environ, start_response)

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
    httpserver = load_paste_httpserver()
    host = os.environ.get('SILVER_SERVE_HOST', '127.0.0.1')
    port = os.environ.get('SILVER_SERVE_PORT', '8080')
    try:
        httpserver.serve(app, host=host, port=port)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    base_path = sys.argv[1]
    main(base_path)
