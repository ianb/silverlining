import os
from silversupport.shell import run, overwrite_file
from silversupport.abstractservice import AbstractService


class Service(AbstractService):

    packages = [
        'postgresql-8.4',
        'postgresql-client',
        'postgresql-client-8.4',
        'postgresql-client-common',
        'postgresql-common',
        ]

    platform_packages = dict(
        python=[
            'python-psycopg2',
            'python-egenix-mxdatetime',
            'python-egenix-mxtools',
            ],
        php=[
            'php5-pgsql',
            ])

    def install(self):
        if not os.path.exists('/usr/bin/psql'):
            self.install_packages()
            overwrite_file('/etc/postgresql/8.4/main/pg_hba.conf',
                           source_file=os.path.join(os.path.dirname(__file__),
                                                    'postgresql-pg_hba.conf'))
            run(['chown', 'postgres:postgres',
                 '/etc/postgresql/8.4/main/pg_hba.conf'])
            run(['/etc/init.d/postgresql-8.4', 'restart'])

        stdout, stderr, returncode = run(
            ['psql', '-U', 'postgres', '--tuples-only'],
            capture_stdout=True, capture_stderr=True,
            stdin="select r.rolname from pg_catalog.pg_roles as r;")
        if 'www-mgr' not in stdout:
            run(['createuser', '-U', 'postgres',
                 '--no-superuser', '--no-createdb',
                 '--no-createrole', 'www-mgr'])

        app_name = self.app_config.app_name
        stdout, stderr, returncode = run(
            ['/usr/bin/psql', '-U', 'postgres', '-l', '-t', '-A'],
            capture_stdout=True)
        databases = [line.split('|')[0] for line in stdout.splitlines()]
        if app_name in databases:
            self.output('Database %s already exists' % app_name)
        else:
            self.output('Database %s does not exist; creating.' % app_name)
            run(['createdb', '-U', 'postgres', '-O', 'www-mgr',
                 app_name])

    def env_setup(self):
        environ = {}
        app_name = self.app_config.app_name
        if not self.devel:
            environ['CONFIG_PG_DBNAME'] = app_name
            environ['CONFIG_PG_USER'] = 'www-mgr'
            environ['CONFIG_PG_PASSWORD'] = ''
            environ['CONFIG_PG_HOST'] = ''
            environ['CONFIG_PG_PORT'] = ''
            environ['CONFIG_PG_SQLALCHEMY'] = 'postgres://postgres@/%s' % app_name
        else:
            import getpass
            environ['CONFIG_PG_DBNAME'] = app_name
            environ['CONFIG_PG_USER'] = getpass.getuser()
            environ['CONFIG_PG_PASSWORD'] = ''
            environ['CONFIG_PG_HOST'] = ''
            environ['CONFIG_PG_PORT'] = ''
            for name, value in self.devel_config.items():
                if name.startswith('postgis.'):
                    name = name[len('postgis.'):]
                    environ['CONFIG_PG_%s' % name.upper()] = value
            sa = 'postgres://'
            if environ.get('CONFIG_PG_USER'):
                sa += environ['CONFIG_PG_USER']
                if environ.get('CONFIG_PG_PASSWORD'):
                    sa += ':' + environ['CONFIG_PG_PASSWORD']
                sa += '@'
            if environ.get('CONFIG_PG_HOST'):
                ## FIXME: should this check for 'localhost', which SA actually doesn't like?
                sa += environ['CONFIG_PG_HOST']
            if environ.get('CONFIG_PG_PORT'):
                sa += ':' + environ['CONFIG_PG_PORT']
            sa += '/' + environ['CONFIG_PG_DBNAME']
            environ['CONFIG_PG_SQLALCHEMY'] = sa
        return environ

    def cli_options(self, force_user=None):
        if not force_user:
            force_user = self.env['CONFIG_PG_USER']
        options = ['-U', force_user]
        if self.env.get('CONFIG_PG_HOST'):
            options.extend(['--host', self.env['CONFIG_PG_HOST']])
            if self.env.get('CONFIG_PG_PORT'):
                options.extend(['--port', self.env['CONFIG_PG_PORT']])
        return options

    def backup(self, output_dir):
        ## FIXME: this includes a bunch of nonsense
        run(['pg_dump', '--format=custom', '--no-owner', '--no-acl', '--no-privileges']
            + self.cli_options('postgres')
            + [self.env['CONFIG_PG_DBNAME'], '--file', os.path.join(output_dir, 'postgis.pgdump')])
        fp = open(os.path.join(output_dir, 'postgis.README.txt'), 'w')
        fp.write(self.BACKUP_README)
        fp.close()

    BACKUP_README = """\
    The backup is created by pg_dump -Fc.  To restore it use pg_restore.
    """

    def restore(self, input_dir):
        path = os.path.join(input_dir, 'postgis.pgdump')
        dbname = self.env['CONFIG_PG_DBNAME']
        run(['pg_restore'] + self.cli_options('postgres') + ['--dbname', dbname, path])

    def clear(self):
        dbname = self.env['CONFIG_PG_DBNAME']
        ## FIXME: -U etc?
        run(['dropdb'] + self.cli_options('postgres') + [dbname])
        self.install()
