"""Cleans out unused instances from a server"""
from silversupport.shell import ssh


def command_clean_node(config):
    if config.args.simulate:
        simulate = '-n'
    else:
        simulate = ''
    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/clean-instances.py %s' % simulate)
