from cmdutils import CommandError
from silversupport.appdata import normalize_location
from silversupport.shell import ssh


def command_disable(config, enable=False):
    node, location, appname = None, None, None
    if config.args.by_name is not None:
        appname = config.args.by_name
    if config.args.by_location is not None:
        location = config.args.by_location
        node, _path = normalize_location(location)
    if config.args.node is not None:
        node = config.node_hostname
    if location and not appname:
        stdout, _stderr, _returncode = ssh(
            'www-mgr', node,
            '/usr/local/share/silverlining/mgr-scripts/get-application.py',
            fail_on_error=True)
        appname = stdout.strip()
    if node is None or appname is None:
        raise CommandError("Unable to determine target node or appname.")
    ssh('www-mgr', node,
        '/usr/local/share/silverlining/mgr-scripts/disable.py %s %s'
        % ('--enable' if enable else '', appname))
