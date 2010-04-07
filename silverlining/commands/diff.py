"""Update/deploy an application"""
import os
import random
from silversupport.shell import ssh
from silversupport.appconfig import AppConfig


def command_diff(config):
    app_config = AppConfig(os.path.join(config.args.dir, 'app.ini'),
                           app_name=config.args.app_name)
    tmp_location = '/tmp/temp-diff-app.%s.%s.%s' % (
        app_config.app_name, random.randint(1, 100000), os.getpid())
    if config.args.instance_name:
        inst = '--instance-name=%s' % config.args.instance_name
    else:
        inst = ''
    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/prepare-temp.py %s %s %s %s'
        % (tmp_location, config.node_hostname, app_config.app_name,
           inst))
    app_config.sync('www-mgr@' + config.node_hostname, tmp_location)
    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/app-diff.py %s %s %s %s'
        % (tmp_location, config.node_hostname, app_config.app_name,
           inst))
