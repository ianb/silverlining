"""Gives a persistent location to keep files"""

import os
import pwd
import grp
import subprocess
import shutil

def dir_for_instance_name(instance_name):
    base = instance_name.split('.')[0]
    dir = os.path.join('/var/lib/toppcloud/apps', base)
    return dir

def install(app_dir, config):
    dir = dir_for_instance_name(app_dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
        uid = pwd.getpwnam('www-data').pw_uid
        gid = grp.getgrnam('www-data').gr_gid
        os.chown(dir, uid, gid)

def app_setup(app_dir, config, environ,
              devel=False, devel_config=None):
    if not devel:
        dir = dir_for_instance_name(app_dir)
        environ['CONFIG_FILES'] = dir
    else:
        app_name = app_dir.split('.')[0]
        environ['CONFIG_FILES'] = os.path.join(
            os.environ['HOME'],
            'toppcloud-app-data',
            app_name)
        if 'files' in devel_config:
            environ['CONFIG_FILES'] = os.path.expanduser(
                devel_config['files'])
        if not os.path.exists(environ['CONFIG_FILES']):
            print 'Creating file location %s' % environ['CONFIG_FILES']
            os.makedirs(environ['CONFIG_FILES'])

def backup(app_dir, config, environ, output_dir):
    path = environ['CONFIG_FILES']
    ## FIXME: should this be compressed, or just rely on that to
    ## happen at a higher level?
    proc = subprocess.Popen(
        ['tar', 'fc', os.path.join(output_dir, 'files.tar'), '.'],
        cwd=path)
    proc.communicate()
    
def restore(app_dir, config, environ, input_dir):
    path = environ['CONFIG_FILES']
    proc = subprocess.Popen(
        ['tar', 'fx', os.path.join(input_dir, 'files.tar')],
        cwd=path)
    proc.communicate()

def clear(app_dir, config, environ):
    path = environ['CONFIG_FILES']
    for p in os.listdir(path):
        p = os.path.join(path, p)
        shutil.rmtree(p)
