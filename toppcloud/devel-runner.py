from site import addsitedir
import sys
import os

def get_app(base_path):
    site = 'localhost'
    os.environ['SITE'] = site
    lib_path = os.path.join(base_path, 'lib', 'python%s' % sys.version[:3],
                            'site-packages')
    if lib_path not in sys.path:
        addsitedir(lib_path)

    # We could do a setup here...
    #for service, config in sorted(common.services_config(site).items()):
    #    common.load_service_module(service).app_setup(site, config, os.environ)

    config_ini = os.path.join(base_path, 'config.ini')
    main_py = os.path.join(base_path, 'main.py')
    if os.path.exists(config_ini):
        from paste.deploy import loadapp
        found_app = loadapp(config_ini)
    elif os.path.exists(main_py):
        ## FIXME: not sure what name to give it
        ns = {'__file__': main_py, '__name__': 'main_py'}
        execfile(main_py, ns)
        if 'application' in ns:
            found_app = ns['application']
        else:
            raise NameError('No application() defined in %s' % main_py)
    else:
        raise OSError("No config.ini or main.py in %s" % base_path)
    return found_app

## FIXME: should do something about reloading

def main(base_path):
    app = get_app(base_path)
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server(
        '127.0.0.1', 8080, app)
    print 'Serving on http://127.0.0.1:8080'
    server.serve_forever()

if __name__ == '__main__':
    base_path = sys.argv[1]
    main(base_path)
