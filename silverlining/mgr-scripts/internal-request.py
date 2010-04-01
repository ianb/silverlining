#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from optparse import OptionParser
import shlex
from silversupport.requests import internal_request
from silversupport.appconfig import AppConfig
from silversupport.shell import run

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


def main():
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
    app_config = AppConfig.from_instance_name(instance_name)
    status, headers, body = internal_request(
        app_config, hostname,
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
    app_config = AppConfig.from_instance_name(instance_name)
    for url in app_config.update_fetch:
        if url.startswith('script:'):
            script = url[len('script:'):]
            print 'Calling update script %s' % script
            call_script(app_config, script)
        else:
            print 'Fetching update URL %s' % url
            app_config.activate_services(os.environ)
            app_config.activate_path()
            status, headers, body = internal_request(
                app_config, hostname,
                url, environ={'silverlining.update': True})
            if not status.startswith('200'):
                sys.stdout.write(status+'\n')
                sys.stdout.flush()
            if body:
                sys.stdout.write(body)
                if not body.endswith('\n'):
                    sys.stdout.write('\n')
                sys.stdout.flush()


def call_script(app_config, script):
    run([sys.executable, os.path.join(os.path.dirname(__file__), 'call-script.py'),
         app_config.app_dir] + shlex.split(script))


if __name__ == '__main__':
    main()
