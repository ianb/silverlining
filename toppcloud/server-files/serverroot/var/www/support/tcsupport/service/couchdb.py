import os
import subprocess

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
    
    # We lower the name because upper-case db names are not allowed in CouchDB
    app_name = app_dir.split('.')[0].lower()
    
    # Ensure that couchdb is installed
    proc = subprocess.Popen(['apt-get', '-y', 'install', 'couchdb', 'python-couchdb'],
                            env=env)
    proc.communicate()
    
    # Check to see if the database is present
    proc = subprocess.Popen(['curl', '-s', '-N', 'http://localhost:5984/_all_dbs'],
                            stdout=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate()
    dbs = eval(stdout)
    
    if app_name in dbs:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; created.' % app_name
        subprocess.Popen([
            'curl', '-N', '-s', '-X', 'PUT', 'http://localhost:5984/%s' % app_name], env=env)
    

def app_setup(app_dir, config, environ):
    app_name = app_dir.split('.')[0].lower()
    environ['COUCHDB_DB'] = app_name
    environ['COUCHDB_HOST'] = '127.0.0.1:5984'
