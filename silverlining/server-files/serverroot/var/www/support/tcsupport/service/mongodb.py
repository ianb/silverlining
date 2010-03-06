import os
import subprocess

import shlex
def run(command,env):
    parts = shlex.split(command)
    proc = subprocess.Popen(parts,env=env)
    return proc.communicate()
    
def install_package(packages,env):
    parts = shlex.split(packages)
    cmd = "apt-get -i install".split()
    cmd.extend(parts)
    return run(cmd,env)

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'
    
    app_name = app_dir.split('.')[0]
    
    #WARNING, this will only work on ubuntu 9.10
    #since we don't have official ubuntu packages we use 10gen's PPA
    run('apt-get -y install python-software-properties',env)#needed for add-apt-repository, perhaps we should just implement a command to append...
    #FIXME, add-apt-repository will duplicate is run twice
    run('add-apt-repository "deb http://downloads.mongodb.org/distros/ubuntu 9.10 10gen"',env)
    run('apt-get update',env)
    run('apt-get -y --force-yes install mongodb',env)
   
    #TODO Check to see if the database is present like couch does, seudo code below

#    stdout,stderr = run('curl -s -N http://localhost:28017/???'
#    dbs = eval(stdout)
    
#    if app_name in dbs:
#        print 'Database %s already exists' % app_name
#    else:
#        print 'Database %s does not exist; created.' % app_name
#        run('curl -N -s -X PUT http://localhost:28017/???' % app_name,env)

def app_setup(app_dir, config, environ,
              devel=False, devel_config=None):
    app_name = app_dir.split('.')[0]
    environ['CONFIG_MONGODB_DB'] = app_name
    environ['CONFIG_MONGODB_HOST'] = '127.0.0.1:5984'
    if devel:
        for name, value in devel_config.items():
            if name.startswith('mongodb.'):
                name = name[len('mongodb.'):]
                environ['CONFIG_MONGODB_%s' % name.upper()] = value
