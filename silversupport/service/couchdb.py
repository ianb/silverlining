import os
import subprocess

def install(app_config, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
    
    # We lower the name because upper-case db names are not allowed in CouchDB
    app_name = app_config.app_name
    
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
