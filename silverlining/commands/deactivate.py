"""Remove an instance from a location"""
from silversupport.shell import ssh
from silversupport import appdata


def command_deactivate(config):
    if not config.args.node:
        config.args.node = appdata.normalize_location(config.args.locations[0])[0]
    if config.args.keep_prev:
        option = ['--keep-prev']
    else:
        option = []
    ssh('www-mgr', config.node_hostname,
        ['/usr/local/share/silverlining/mgr-scripts/remove-host.py']
        + option + config.args.locations)
