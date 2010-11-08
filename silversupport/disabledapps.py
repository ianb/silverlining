"""Routines for managing the list of disabled applications"""

# The file contains application names rather than instance names or locations,
# as what we really care about is databases, and they are shared between
# deployments of the same application.

# The format of the disabled apps file is at present simply a list of
# application names.  In the future it might well be desirable to extend this
# with options for the DisabledSite WSGI middleware, such as a list of IPs
# which can be allowed to access the site, or a set of http auth credentials
# which allow access.  Happily the file should be empty except in exceptional
# circumstances, and we can therefore just change the data format without
# concern for backwards compatibility.

import os.path


DISABLED_APPS_FILE = '/var/www/disabledapps.txt'


class DisabledSite(object):
    """This WSGI app is returned instead of our application when it is disabled
    """

    def __init__(self, real_app, disabled_app):
        self._app = real_app
        self._disabled = disabled_app

    def __call__(self, environ, start_response):
        """Delegates to the disabled app unless some conditions are met"""
        if environ.get('silverlining.update'):
            return self._app(environ, start_response)
        # Allow connections from localhost.
        client = environ['REMOTE_ADDR']
        if client.strip() in ('localhost', '127.0.0.1'):
            return self._app(environ, start_response)
        return self._disabled(environ, start_response)


def is_disabled(application_name):
    """Return True if the application has been disabled"""
    if not os.path.exists(DISABLED_APPS_FILE):
        return False
    with open(DISABLED_APPS_FILE) as file_:
        lines = [line.strip() for line in file_]
        return application_name in lines


def disable_application(application_name):
    """Adds application_name to the list of disabled applications"""
    if not is_disabled(application_name):
        with open(DISABLED_APPS_FILE, 'a') as file_:
            file_.write(application_name)
            file_.write('\n')


def enable_application(application_name):
    """Removes application_name from the list of disabled applications"""
    lines = []
    with open(DISABLED_APPS_FILE, 'r') as file_:
        for line in file_:
            line = line.strip()
            if line != application_name:
                lines.append(line)
    with open(DISABLED_APPS_FILE, 'w') as file_:
        file_.write('\n'.join(lines))
