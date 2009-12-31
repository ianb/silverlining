"""Gives a persistent location to keep files"""

import os
import pwd
import grp

def dir_for_instance_name(instance_name):
    base = instance_name.split('.')[0]
    dir = os.path.join('/var/lib/toppcloud', base)
    return dir

def install(app_dir, config):
    dir = dir_for_instance_name(app_dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
        uid = pwd.getpwnam('www-mgr').pw_uid
        gid = grp.getgrnam('www-mgr').gr_gid
        os.chown(dir, uid, gid)

def app_setup(app_dir, config, environ):
    dir = dir_for_instance_name(app_dir)
    environ['FILES'] = dir

