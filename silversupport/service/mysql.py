"""MySQL support"""

import os
from silversupport.shell import apt_install, run

packages = [
    'mysql-server-5.1',
    'mysql-client-5.1',
    'python-mysqldb',
    ]

platform_packages = dict(
    python=['python-mysqldb'],
    php=['php5-mysql'],
    )


def install(app_config, config):
    if not os.path.exists('/usr/bin/mysqld_multi'):
        apt_install(packages + platform_packages[app_config.platform])
        run(['/usr/bin/mysql', '-u', 'root',
             '-e', 'CREATE USER wwwmgr'])
        if app_config.platform == 'php':
            # We need to restart Apache after installing php5-mysql
            run(['/etc/init.d/apache2', 'restart'])

    app_name = app_config.app_name
    stdout, stderr, returncode = run(
        ['/usr/bin/mysql', '-u', 'root',
         '-e', 'SHOW DATABASES', '--batch', '-s'],
        capture_stdout=True)
    databases = [l.strip() for l in stdout.splitlines() if l.strip()]
    if app_name in databases:
        print 'Database %s already exists' % app_name
    else:
        print 'Database %s does not exist; creating.' % app_name
        run(['/usr/bin/mysql', '-u', 'root',
             '-e', 'CREATE DATABASE %s' % app_name])
        run(['/usr/bin/mysql', '-u', 'root',
             '-e', "GRANT ALL ON %s.* TO 'wwwmgr'@'localhost'" % app_name])


def app_setup(app_config, config, environ,
              devel=False, devel_config=None):
    app_name = app_config.app_name
    platform = app_config.platform
    if not devel:
        environ['CONFIG_MYSQL_DBNAME'] = app_name
        environ['CONFIG_MYSQL_USER'] = 'wwwmgr'
        environ['CONFIG_MYSQL_PASSWORD'] = ''
        if platform == 'php':
            environ['CONFIG_MYSQL_HOST'] = 'localhost'
        else:
            environ['CONFIG_MYSQL_HOST'] = ''
        environ['CONFIG_MYSQL_PORT'] = ''
        if platform == 'python':
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


def backup(app_config, config, environ, output_dir):
    raise NotImplemented

BACKUP_README = """\
FIXME
"""


def restore(app_config, config, environ, input_dir):
    raise NotImplemented


def mysql_options(environ):
    options = []
    options.append('--user=%s' % environ['CONFIG_MYSQL_USER'])
    for option, key in [('password', 'PASSWORD'),
                        ('user', 'USER'),
                        ('host', 'HOST'),
                        ('port', 'PORT')]:
        if environ.get('CONFIG_MYSQL_%s' % key):
            options.append('--%s=%s' % (option, environ['CONFIG_MYSQL_%s' % key]))
    options.append(environ['CONFIG_MYSQL_DBNAME'])
    return options


def clear(app_config, config, environ):
    run(["mysql"] + mysql_options(environ),
        stdin='DROP DATABASE %s' % environ['CONFIG_MYSQL_DBNAME'])
    install(app_config, config)
    print 'Cleared database %s' % environ['CONFIG_MYSQL_DBNAME']
