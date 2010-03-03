"""Gives a persistent location to keep files"""

import os
import pwd
import grp
import subprocess
import shutil

class FileService(object):
    def __init__(self, root, env_var):
        self.root = root
        self.env_var = env_var

    def dir_for_instance_name(self, instance_name):
        base = instance_name.split('.')[0]
        dir = os.path.join(self.root, base)
        return dir

    def install(self, app_dir, config):
        dir = self.dir_for_instance_name(app_dir)
        if not os.path.exists(dir):
            os.makedirs(dir)
            uid = pwd.getpwnam('www-data').pw_uid
            gid = grp.getgrnam('www-data').gr_gid
            os.chown(dir, uid, gid)

    def app_setup(self, app_dir, config, environ,
                  devel=False, devel_config=None):
        if not devel:
            dir = self.dir_for_instance_name(app_dir)
            environ[self.env_var] = dir
        else:
            app_name = app_dir.split('.')[0]
            environ[self.env_var] = os.path.join(
                os.environ['HOME'],
                '.silverlining-app-data',
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
        proc = subprocess.Popen(
            ['tar', 'fc', os.path.join(output_dir, 'files.tar'), '.'],
            cwd=path)
        proc.communicate()

    def restore(self, app_dir, config, environ, input_dir):
        path = environ[self.env_var]
        proc = subprocess.Popen(
            ['tar', 'fx', os.path.join(input_dir, 'files.tar')],
            cwd=path)
        proc.communicate()

    def clear(self, app_dir, config, environ):
        path = environ[self.env_var]
        for p in os.listdir(path):
            p = os.path.join(path, p)
            shutil.rmtree(p)

service = FileService(
    '/var/lib/silverlining/apps', 'CONFIG_FILES')
install = service.install
app_setup = service.app_setup
backup = service.backup
restore = service.restore
clear = service.clear
