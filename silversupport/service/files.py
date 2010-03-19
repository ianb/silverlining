"""Gives a persistent location to keep files"""

import os
import pwd
import grp
import shutil
from silversupport.shell import run


class FileService(object):
    """Abstract class that can be used for internal and public files"""

    def __init__(self, root, env_var, home_name):
        self.root = root
        self.env_var = env_var
        self.home_name = home_name

    def dir_for_app_name(self, app_name):
        return os.path.join(self.root, app_name)

    def install(self, app_config, config):
        dir = self.dir_for_app_name(app_config.app_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
            uid = pwd.getpwnam('www-data').pw_uid
            gid = grp.getgrnam('www-data').gr_gid
            os.chown(dir, uid, gid)

    def app_setup(self, app_config, config, environ,
                  devel=False, devel_config=None):
        app_name = app_config.app_name
        if not devel:
            dir = self.dir_for_app_name(app_name)
            environ[self.env_var] = dir
        else:
            environ[self.env_var] = os.path.join(
                os.environ['HOME'],
                '.silverlining-app-data',
                self.home_name,
                app_name)
            if 'files' in devel_config:
                environ[self.env_var] = os.path.expanduser(
                    devel_config['files'])
            if not os.path.exists(environ[self.env_var]):
                print 'Creating file location %s' % environ[self.env_var]
                os.makedirs(environ[self.env_var])

    def backup(self, app_dir, config, environ, output_dir):
        path = environ[self.env_var]
        ## FIXME: should this be compressed, or just rely on that to
        ## happen at a higher level?
        run(['tar', 'fc', os.path.join(output_dir, 'files.tar'), '.'],
            cwd=path)

    def restore(self, app_dir, config, environ, input_dir):
        path = environ[self.env_var]
        run(['tar', 'fx', os.path.join(input_dir, 'files.tar')],
            cwd=path)

    def clear(self, app_dir, config, environ):
        path = environ[self.env_var]
        for p in os.listdir(path):
            p = os.path.join(path, p)
            shutil.rmtree(p)

service = FileService(
    '/var/lib/silverlining/apps', 'CONFIG_FILES', 'files')
install = service.install
app_setup = service.app_setup
backup = service.backup
restore = service.restore
clear = service.clear
