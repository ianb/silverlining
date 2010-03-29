"""MySQL support"""

import os
from silversupport.shell import run
from silversupport.abstractservice import AbstractService


class Service(AbstractService):

    packages = [
        'mysql-server-5.1',
        'mysql-client-5.1',
        'python-mysqldb',
        ]

    platform_packages = dict(
        python=['python-mysqldb'],
        php=['php5-mysql'],
        )

    def install(self):
        if not os.path.exists('/usr/bin/mysqld_multi'):
            self.install_packages()
            run(['/usr/bin/mysql', '-u', 'root',
                 '-e', 'CREATE USER wwwmgr'])
            if self.app_config.platform == 'php':
                # We need to restart Apache after installing php5-mysql
                run(['/etc/init.d/apache2', 'restart'])

        app_name = self.app_config.app_name
        stdout, stderr, returncode = run(
            ['/usr/bin/mysql', '-u', 'root',
             '-e', 'SHOW DATABASES', '--batch', '-s'],
            capture_stdout=True)
        databases = [l.strip() for l in stdout.splitlines() if l.strip()]
        if app_name in databases:
            self.output('Database %s already exists' % app_name)
        else:
            self.output('Database %s does not exist; creating.' % app_name)
            run(['/usr/bin/mysql', '-u', 'root',
                 '-e', 'CREATE DATABASE %s' % app_name])
            run(['/usr/bin/mysql', '-u', 'root',
                 '-e', "GRANT ALL ON %s.* TO 'wwwmgr'@'localhost'" % app_name])

    def env_setup(self):
        environ = {}
        app_name = self.app_config.app_name
        platform = self.app_config.platform
        if not self.devel:
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
            for name, value in self.devel_config.items():
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
        return environ

    def backup(self, output_dir):
        outfile = os.path.join(output_dir, 'mysql.dump')
        run(["mysqldump"] + self.mysql_options() + ['--result-file', outfile])
        fp = open(os.path.join(output_dir, 'README.txt'), 'w')
        fp.write(self.BACKUP_README)
        fp.close()

    BACKUP_README = """\
    The file mysql.dump was created with mysqldump; you can pip it into
    mysql to restore.
    """

    def restore(self, input_dir):
        input_file = os.path.join(input_dir, 'mysql.dump')
        fp = open(input_file)
        content = fp.read()
        fp.close()
        run(['mysql'] + self.mysql_options() + ['--silent'],
            stdin=content)

    def mysql_options(self):
        environ = self.env
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

    def clear(self):
        run(["mysql"] + self.mysql_options(),
            stdin='DROP DATABASE %s' % self.env['CONFIG_MYSQL_DBNAME'])
        self.install()
        self.output('Cleared database %s' % self.env['CONFIG_MYSQL_DBNAME'])
