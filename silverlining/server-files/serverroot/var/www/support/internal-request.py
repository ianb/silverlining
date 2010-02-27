#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tcsupport.requests import make_internal_request, create_app
from ConfigParser import ConfigParser
from optparse import OptionParser

parser = OptionParser(
    usage="%prog (--update INSTANCE_NAME) or (INSTANCE_NAME HOSTNAME PATH VAR1=value VAR2=value)",
    description="""\
Make an internal request.  If --update is given then an internal
request according to the update_fetch configuration in app.ini will be
run.

Without --update, an arbitrary request will be run.  This request will
be run on the given INSTANCE_NAME regardless of hostmap.txt.  Thus you
can run requests on apps that have not been fully activated.  Any
VAR=value assignments will go into the request environ.
""")

parser.add_option(
    '--update',
    action='store_true',
    help="Run the update_fetch command on the given app_name")

def run():
    """Run the command, making an internal request"""
    options, args = parser.parse_args()
    if options.update:
        return run_update(args[0], args[1])
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
    """Run the --update command, running any request configured with
    update_fetch in app.ini"""
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
                url, environ={'silverlining.update': True})
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
