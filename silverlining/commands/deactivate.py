from silverlining.util import ssh

def command_deactivate(config):
    if not config.args.node:
        config.args.node = config.args.hosts[0]
    if config.args.disable:
        for host in config.args.hosts:
            ssh('www-mgr', config.args.host,
                '/var/www/support/activate-host.py %s disabled'
                % host)
    else:
        if config.args.keep_prev:
            option = '--keep-prev'
        else:
            option = ''
        ssh('www-mgr', config.node_hostname,
            '/var/www/support/remove-host.py %s %s'
            % (option, ' '.join(config.args.hosts)))
