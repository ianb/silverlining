"""Routines to activate instances for specific locations"""
from silversupport.shell import ssh
from silveruspport import appdata


def command_activate(config):
    if not config.args.node:
        config.args.node = appdata.normalize_location(config.args.location)[0]
    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/activate-instance.py %s %s' %
        (config.args.location, config.args.instance_name))
