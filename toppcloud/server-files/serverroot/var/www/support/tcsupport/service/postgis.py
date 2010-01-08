import os
import subprocess

packages = [
    'postgis',
    'postgresql-8.3',
    'postgresql-8.3-postgis',
    'postgresql-client',
    'postgresql-client-8.3',
    'postgresql-client-common',
    'postgresql-common',
    'python-psycopg2',
    'python-egenix-mxdatetime',
    'python-egenix-mxtools',
    'python-gdal',
    'proj',
    'python-pyproj',
    'python-pyproj-data',
    ]

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
    env['PGUSER'] = 'postgres'

    if not os.path.exists('/usr/bin/psql'):
        proc = subprocess.Popen(
            ['chown', 'postgres:postgres',
             '/etc/postgresql/8.3/main/pg_hba.conf'],
            env=env)
        proc.communicate()
        proc = subprocess.Popen(
            ['apt-get', '-y', 'install'] + packages,
            env=env)
        proc.communicate()
    proc = subprocess.Popen(
        ['psql', '--tuples-only'],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE,
        env=env)
    stdout, stderr = proc.communicate("""
    select r.rolname from pg_catalog.pg_roles as r;
    """)
    if 'www-mgr' not in stdout:
        proc = subprocess.Popen(
            ['createuser', '--no-superuser', '--no-createdb',
             '--no-createrole', 'www-mgr'], env=env)
        proc.communicate()
        
    proc = subprocess.Popen(
        ['psql', '-l'], stdout=subprocess.PIPE,
        env=env)
    stdout, stderr = proc.communicate()
    if 'template_postgis' not in stdout:
        proc = subprocess.Popen(
            ['createdb', 'template_postgis'],
            env=env)
        proc.communicate()
        proc = subprocess.Popen(
            ['psql', 'template_postgis'],
            env=env, stdin=subprocess.PIPE)
        parts = ['CREATE LANGUAGE plpgsql;\n']
        for filename in ['lwpostgis.sql', 'lwpostgis_upgrade.sql',
                         'spatial_ref_sys.sql']:
            filename = os.path.join(
                '/usr/share/postgresql-8.3-postgis', filename)
            fp = open(filename)
            parts.append(fp.read())
            parts.append('\n;\n')
            fp.close()
        proc.communicate(''.join(parts))
    
    app_name = app_dir.split('.')[0]
    proc = subprocess.Popen([
        '/usr/bin/psql', '-U', 'postgres', '-l', '-t', '-A'], 
        stdout=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate()
    databases = [line.split('|')[0] for line in stdout.splitlines()]
    if app_name in databases:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; creating.' % app_name
        proc = subprocess.Popen(
            ['createdb', '-O', 'www-mgr', '-T', 'template_postgis',
             app_name], env=env)
        proc.communicate()

def app_setup(app_dir, config, environ,
              devel=False, devel_config=None):
    app_name = app_dir.split('.')[0]
    if not devel:
        environ['CONFIG_PG_DBNAME'] = app_name
        environ['CONFIG_PG_USER'] = 'www-mgr'
        environ['CONFIG_PG_PASSWORD'] = ''
        environ['CONFIG_PG_HOST'] = ''
    else:
        import getpass
        environ['CONFIG_PG_DBNAME'] = app_name
        environ['CONFIG_PG_USER'] = getpass.getuser()
        environ['CONFIG_PG_PASSWORD'] = ''
        environ['CONFIG_PG_HOST'] = ''
        for name, value in devel_config.items():
            if name.startswith('postgis.'):
                name = name[len('postgis.'):]
                environ['CONFIG_PG_%s' % name.upper()] = value
                
