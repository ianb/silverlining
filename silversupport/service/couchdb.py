"""CouchDB service support"""

from json import loads
from silversupport.shell import run, apt_install


def install(app_config, config):
    # We lower the name because upper-case db names are not allowed in CouchDB
    app_name = app_config.app_name.lower()

    # Ensure that couchdb is installed
    apt_install(['couchdb', 'python-couchdb'])

    # Check to see if the database is present
    stdout, stderr, returncode = run(
        ['curl', '-s', '-N', 'http://localhost:5984/_all_dbs'],
        capture_stdout=True)
    dbs = loads(stdout)

    if app_name in dbs:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; created.' % app_name
        run(['curl', '-N', '-s', '-X', 'PUT', 'http://localhost:5984/%s' % app_name])


def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    app_name = app_config.app_name
    environ['CONFIG_COUCHDB_DB'] = app_name
    environ['CONFIG_COUCHDB_HOST'] = '127.0.0.1:5984'
    if devel:
        for name, value in devel_config.items():
            if name.startswith('couchdb.'):
                name = name[len('couchdb.'):]
                environ['CONFIG_COUCHDB_%s' % name.upper()] = value
