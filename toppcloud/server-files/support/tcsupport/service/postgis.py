import os
import subprocess

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
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
