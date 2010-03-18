import os
import subprocess

packages = [
    'mysql-server-5.1',
    'mysql-client-5.1',
    'python-mysqldb',
    ]

def install(app_dir, config):
    env = os.environ.copy()
    env['LANG'] = 'C'

    if not os.path.exists('/usr/bin/mysqld_multi'):
        proc = subprocess.Popen(
            ['apt-get', '-y', 'install'] + packages,
            env=env)
        proc.communicate()
        proc = subprocess.Popen(
            ['/usr/bin/mysql', '-u', 'root',
             '-e', 'CREATE USER wwwmgr'])
    
    app_name = app_dir.split('.')[0]
    proc = subprocess.Popen(
        ['/usr/bin/mysql', '-u', 'root',
         '-e', 'SHOW DATABASES', '--batch', '-s'],
        stdout=subprocess.PIPE, env=env)
    stdout, stderr = proc.communicate()
    databases = [l.strip() for l in stdout.splitlines() if l.strip()]
    if app_name in databases:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; creating.' % app_name
        proc = subprocess.Popen(
            ['/usr/bin/mysql', '-u', 'root',
             '-e', 'CREATE DATABASE %s' % app_name,],
            env=env)
        proc.communicate()
        proc = subprocess.Popen(
            ['/usr/bin/mysql', '-u', 'root',
             '-e', "GRANT ALL ON %s.* TO 'wwwmgr'@'localhost'" % app_name],
            env=env)
        proc.communicate()

def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    app_name = app_config.app_name
    if not devel:
        environ['CONFIG_MYSQL_DBNAME'] = app_name
        environ['CONFIG_MYSQL_USER'] = 'wwwmgr'
        environ['CONFIG_MYSQL_PASSWORD'] = ''
        environ['CONFIG_MYSQL_HOST'] = ''
        environ['CONFIG_MYSQL_PORT'] = ''
        environ['CONFIG_MYSQL_SQLALCHEMY'] = 'mysql://wwwmgr@/%s' % app_name
    else:
        environ['CONFIG_MYSQL_DBNAME'] = app_name
        environ['CONFIG_MYSQL_USER'] = 'root'
        environ['CONFIG_MYSQL_PASSWORD'] = ''
        environ['CONFIG_MYSQL_HOST'] = ''
        environ['CONFIG_MYSQL_PORT'] = ''
        for name, value in devel_config.items():
            if name.startswith('mysql.'):
                name = name[len('mysql.'):]
                environ['CONFIG_MYSQL_%s' % name.upper()] = value
        sa = 'mysql://'
        if environ.get('CONFIG_MYSQL_USER'):
            sa += environ['CONFIG_MYSQL_USER']
            if environ.get('CONFIG_MYSQL_PASSWORD'):
                sa += ':' + environ['CONFIG_MYSQL_PASSWORD']
            sa += '@'
        if environ.get('CONFIG_MYSQL_HOST'):
            ## FIXME: should this check for 'localhost', which SA actually doesn't like?
            sa += environ['CONFIG_MYSQL_HOST']
        if environ.get('CONFIG_MYSQL_PORT'):
            sa += ':' + environ['CONFIG_MYSQL_PORT']
        sa += '/' + environ['CONFIG_MYSQL_DBNAME']
        environ['CONFIG_MYSQL_SQLALCHEMY'] = sa
                
def backup(app_dir, config, environ, output_dir):
    raise NotImplemented

BACKUP_README = """\
FIXME
"""

def restore(app_dir, config, environ, input_dir):
    raise NotImplemented

def clear(app_dir, config, environ):
    raise NotImplemented
    
