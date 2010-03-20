"""Remove an instance from a location"""
from silversupport.shell import ssh
from silversupport import appdata


def command_deactivate(config):
    if not config.args.node:
        config.args.node = appdata.normalize_location(config.args.locations[0])[0]
    if config.args.disable:
        for location in config.args.locations:
            ssh('www-mgr', config.args.host,
                '/usr/local/share/silverlining/mgr-scripts/activate-instance.py %s disabled'
                % location)
    else:
        if config.args.keep_prev:
            option = ['--keep-prev']
        else:
            option = []
        ssh('www-mgr', config.node_hostname,
            ['/usr/local/share/silverlining/mgr-scripts/remove-host.py']
            + option + config.args.locations)
