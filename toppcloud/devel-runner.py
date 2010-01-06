from site import addsitedir
import sys
import os
from ConfigParser import ConfigParser
import posixpath
path = os.path.join(
    os.path.dirname(__file__),
    'server-files/serverroot/var/www/support')
sys.path.insert(0, path)
from tcsupport import common

toppcloud_conf = os.path.join(os.environ['HOME'], '.toppcloud.conf')

def get_app(base_path):
    site = 'localhost'
    os.environ['SITE'] = site
    lib_path = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                            'site-packages')
    if lib_path not in sys.path:
        addsitedir(lib_path)

    parser = ConfigParser()
    parser.read([os.path.join(base_path, 'app.ini')])
    if not parser.has_option('production', 'runner'):
        raise Exception(
            "No option 'runner' in [production]")
    runner = parser.get('production', 'runner')
    if '#' in runner:
        runner, spec = runner.split('#', 1)
    else:
        spec = None
    runner = os.path.join(base_path, runner)
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
            "Unknown kind of runner (%s)" % runner)(environ, start_response)
    app_name = parser.get('production', 'app_name')

    global_parser = ConfigParser()
    global_parser.read([toppcloud_conf])
    if global_parser.has_section('devel:%s' % app_name):
        section = 'devel:%s' % app_name
    elif global_parser.has_section('devel'):
        section = 'devel'
    else:
        section = None
    config = {}
    if not section:
        print 'Warning: %s has no [devel] section to configure your services' % (
            toppcloud_conf)
    else:
        for name in global_parser.options(section):
            value = global_parser.get(section, name)
            config[name] = value.replace('APP_NAME', app_name)

    for service, config in sorted(common.services_config(None, parser=parser).items()):
        common.load_service_module(service).app_setup(
            app_name, config, os.environ, devel=True,
            devel_config=config)
    
    return found_app

def compound_app(base_path):
    app = get_app(base_path)
    from paste.cascade import Cascade
    from paste.urlparser import StaticURLParser
    static_app = StaticURLParser(os.path.join(base_path, 'static'))
    compound_app = Cascade([static_app, app])
    return compound_app

## FIXME: should do something about reloading

def main(base_path):
    app = compound_app(base_path)
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server(
        '127.0.0.1', 8080, app)
    print 'Serving on http://127.0.0.1:8080'
    server.serve_forever()

if __name__ == '__main__':
    base_path = sys.argv[1]
    main(base_path)
