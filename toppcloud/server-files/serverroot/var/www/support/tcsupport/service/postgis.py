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

    proc = subprocess.Popen(
        ['apt-get', '-y', 'install'] + packages,
        env=env)
    proc.communicate()
    
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
        subprocess.Popen([
            'createdb', '-U', 'www-mgr', '-T', 'template_postgis',
            app_name], env=env)

def app_setup(app_dir, config, environ):
    app_name = app_dir.split('.')[0]
    environ['PG_DBNAME'] = app_name
    environ['PG_USER'] = 'www-mgr'
    environ['PG_PASSWORD'] = ''
    environ['PG_HOST'] = ''
