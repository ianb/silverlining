from site import addsitedir
import sys
import os
from ConfigParser import ConfigParser
path = os.path.join(
    os.path.dirname(__file__),
    'server-files/serverroot/var/www/support')
sys.path.insert(0, path)
# The parent directory ends up on sys.path, even though we don't want
# it to; here we remove it:
here = os.path.abspath(os.path.dirname(__file__))
for path in list(sys.path):
    if os.path.abspath(path) == here:
        sys.path.remove(path)
from tcsupport import common
from tcsupport.requests import make_internal_request
from tcsupport.develconfig import load_devel_config
import mimetypes

toppcloud_conf = os.path.join(os.environ['HOME'], '.toppcloud.conf')

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
    site = 'localhost'
    os.environ['SITE'] = site
    lib_path = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                            'site-packages')
    if lib_path not in sys.path:
        addsitedir(lib_path)
    sitecustomize = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                                 'sitecustomize.py')
    if os.path.exists(sitecustomize):
        ns = {'__file__': sitecustomize, '__name__': 'sitecustomize'}
        execfile(sitecustomize, ns)

    parser = ConfigParser()
    app_ini = os.path.join(base_path, 'app.ini')
    parser.read([app_ini])
    reloader.watch_file(app_ini)
    app_name = parser.get('production', 'app_name')

    devel_config = load_devel_config(app_name)

    for service, config in sorted(common.services_config(None, parser=parser).items()):
        common.load_service_module(service).app_setup(
            app_name, config, os.environ, devel=True,
            devel_config=devel_config)

    if not parser.has_option('production', 'runner'):
        raise Exception(
            "No option 'runner' in [production]")
    runner = parser.get('production', 'runner')
    if '#' in runner:
        runner, spec = runner.split('#', 1)
    else:
        spec = None
    runner = os.path.join(base_path, runner)
    reloader.watch_file(runner)
    if not os.path.exists(runner):
        raise Exception(
            "The setting ([production] runner) points to the file %s which does not exist"
            % runner)
    ## FIXME: copied from master_runner.py, which is lame
    if runner.endswith('.ini'):
        from paste.deploy import loadapp
        runner = 'config:%s' % runner
        global_conf = os.environ.copy()
        ## FIXME: less fake?
        global_conf['SECRET'] = '1234567890'
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
            raise NameError(
                "No application %s defined in %s"
                % (runner, spec))
    elif runner.startswith('static'):
        raise Exception("not supported with toppcloud serve")
    else:
        raise Exception(
            "Unknown kind of runner (%s)" % runner)

    if parser.has_option('production', 'update_fetch'):
        urls = parser.get('production', 'update_fetch')
        urls = [url for url in urls.splitlines()
                if url.strip() and not url.strip().startswith('#')]
        for url in urls:
            print 'Fetching update URL %s' % url
            status, headers, body = make_internal_request(
                found_app, app_name, 'localhost',
                url, environ={'toppcloud.update': True})
            if not status.startswith('200'):
                sys.stdout.write(status+'\n')
                sys.stdout.flush()
            if body:
                sys.stdout.write(body)
                if not body.endswith('\n'):
                    sys.stdout.write('\n')
                sys.stdout.flush()
    
    return found_app

class CompoundApp(object):

    def __init__(self, base_path):
        self.base_path = base_path
        self.app = get_app(base_path)

    def __call__(self, environ, start_response):
        environ['toppcloud.devel'] = True
        path_info = environ.get('PATH_INFO', '')
        path_info = os.path.normpath(path_info)
        path_info = path_info.replace('\\', '/').lstrip('/')
        path = os.path.join(self.base_path, 'static', path_info)
        ## FIXME: this should redirect (add / etc) same as wsgi_runner does:
        if os.path.exists(path) and os.path.isdir(path) and os.path.exists(os.path.join(path, 'index.html')):
            return self.serve_file(os.path.join(path, 'index.html'), environ, start_response)
        if os.path.exists(path) and not os.path.isdir(path):
            return self.serve_file(path, environ, start_response)
        return self.app(environ, start_response)

    def serve_file(self, path, environ, start_response):
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
