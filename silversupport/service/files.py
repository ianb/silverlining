"""Gives a persistent location to keep files"""

import os
import pwd
import grp
import shutil
from silversupport.shell import run
from silversupport.abstractservice import AbstractService


class AbstractFileService(AbstractService):

    root = None
    env_var = None
    home_name = None

    def dir_for_app_name(self, app_name):
        return os.path.join(self.root, app_name)

    def install(self):
        dir = self.dir_for_app_name(self.app_config.app_name)
        if not os.path.exists(dir):
            os.makedirs(dir)
            uid = pwd.getpwnam('www-data').pw_uid
            gid = grp.getgrnam('www-data').gr_gid
            os.chown(dir, uid, gid)

    def env_setup(self):
        environ = {}
        app_name = self.app_config.app_name
        if not self.devel:
            dir = self.dir_for_app_name(app_name)
            environ[self.env_var] = dir
        else:
            environ[self.env_var] = os.path.join(
                os.environ['HOME'],
                '.silverlining-app-data',
                self.home_name,
                app_name)
            if 'files' in self.devel_config:
                environ[self.env_var] = os.path.expanduser(
                    self.devel_config['files'])
            if not os.path.exists(environ[self.env_var]):
                print 'Creating file location %s' % environ[self.env_var]
                os.makedirs(environ[self.env_var])
        return environ

    def backup(self, output_dir):
        path = self.env[self.env_var]
        ## FIXME: should this be compressed, or just rely on that to
        ## happen at a higher level?
        ## Or should it be a tar at all, or just a copy of the files?
        run(['tar', 'fc', os.path.join(output_dir, 'files.tar'), '.'],
            cwd=path, fail_on_error=True)

    def restore(self, input_dir):
        path = self.env[self.env_var]
        tar_path = os.path.join(input_dir, 'files.tar')
        run(['sudo', '-u', 'www-data', 'tar', 'fx', tar_path],
            cwd=path, fail_on_error=True)

    def clear(self):
        path = self.env[self.env_var]
        for p in os.listdir(path):
            p = os.path.join(path, p)
            shutil.rmtree(p)


class Service(AbstractFileService):
    root = '/var/lib/silverlining/apps'
    env_var = 'CONFIG_FILES'
    home_name = 'files'
