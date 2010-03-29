"""CouchDB service support"""

from json import loads
from silversupport.shell import run
from silversupport.abstractservice import AbstractService


class Service(AbstractService):

    packages = ['couchdb']
    platform_packages = dict(python=['python-couchdb'])

    def install(self):
        # We lower the name because upper-case db names are not allowed in CouchDB
        app_name = self.app_config.app_name.lower()

        # Ensure that couchdb is installed
        self.install_packages()

        # Check to see if the database is present
        stdout, stderr, returncode = run(
            ['curl', '-s', '-N', 'http://localhost:5984/_all_dbs'],
            capture_stdout=True)
        dbs = loads(stdout)

        if app_name in dbs:
            self.output('Database %s already exists' % app_name)
        else:
            self.output('Database %s does not exist; created.' % app_name)
            run(['curl', '-N', '-s', '-X', 'PUT', 'http://localhost:5984/%s' % app_name])

    def env_setup(self):
        environ = {}
        app_name = self.app_config.app_name
        environ['CONFIG_COUCHDB_DB'] = app_name
        environ['CONFIG_COUCHDB_HOST'] = '127.0.0.1:5984'
        if self.devel:
            for name, value in self.devel_config.items():
                if name.startswith('couchdb.'):
                    name = name[len('couchdb.'):]
                    environ['CONFIG_COUCHDB_%s' % name.upper()] = value
        return environ
