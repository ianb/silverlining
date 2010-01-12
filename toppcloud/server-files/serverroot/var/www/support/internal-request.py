#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.requests import make_internal_request, create_app
from ConfigParser import ConfigParser

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
    app = create_app(instance_name)
    status, headers, body = make_internal_request(
        app, instance_name, hostname,
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
            app = create_app(instance_name)
            status, headers, body = make_internal_request(
                app, instance_name, hostname,
                url, environ={'toppcloud.update': True})
            if not status.startswith('200'):
                sys.stdout.write(status+'\n')
                sys.stdout.flush()
            if body:
                sys.stdout.write(body)
                if not body.endswith('\n'):
                    sys.stdout.write('\n')
                sys.stdout.flush()

if __name__ == '__main__':
    run()
