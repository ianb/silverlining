from silverlining.util import ssh

def command_clean_node(config):
    if config.args.simulate:
        simulate = '-n'
    else:
        simulate = ''
    ssh('www-mgr', config.node_hostname,
        '/var/www/support/cleanup-apps.py %s' % simulate)
