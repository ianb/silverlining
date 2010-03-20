"""Routines to activate instances for specific locations"""
from silversupport.shell import ssh


def command_activate(config):
    if not config.args.node:
        config.args.node = config.args.host
    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/activate-instance.py %s %s' %
        (config.args.host, config.args.instance_name))
