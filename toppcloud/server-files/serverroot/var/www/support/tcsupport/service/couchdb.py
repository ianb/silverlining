import os
import subprocess

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
    
    # We lower the name because upper-case db names are not allowed in CouchDB
    app_name = app_dir.split('.')[0].lower()
    
    # Ensure that couchdb is installed
    proc = subprocess.Popen([
'''\
if [ -e /usr/bin/couchdb ] ; then
    exit 50
fi
apt-get -y install couchdb python-couchdb
    ''',])
    proc.communicate()
    
    # Check to see if the database is present
    proc = subprocess.Popen(['curl','http://localhost:5984/_all_dbs'], stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    dbs = eval(stdout)
    
    if app_name in dbs:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; created.' % app_name
        subprocess.Popen([
            'curl', '-X PUT', 'http://localhost:5984/%s' % app_name])
    

def app_setup(app_dir, config, environ):
    app_name = app_dir.split('.')[0].lower()
    environ['COUCHDB_DB'] = app_name
    environ['COUCHDB_HOST'] = '127.0.0.1:5984'
