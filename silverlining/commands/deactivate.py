"""Remove an instance from a location"""
from silversupport.shell import ssh


def command_deactivate(config):
    if not config.args.node:
        config.args.node = config.args.hosts[0]
    if config.args.disable:
        for host in config.args.hosts:
            ssh('www-mgr', config.args.host,
                '/usr/local/share/silverlining/mgr-scripts/activate-host.py %s disabled'
                % host)
    else:
        if config.args.keep_prev:
            option = ['--keep-prev']
        else:
            option = []
        ssh('www-mgr', config.node_hostname,
            ['/usr/local/share/silverlining/mgr-scripts/remove-host.py']
            + option + config.args.hosts)
