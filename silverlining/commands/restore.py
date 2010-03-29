"""Cleans out unused instances from a server"""
from cmdutils import CommandError
from silversupport.shell import ssh, run
from silversupport.appdata import normalize_location
from silversupport import transfermethods


def command_restore(config):
    backup = config.args.backup
    hostname, path = normalize_location(config.args.location)
    dir = move_backup_to_server(backup, hostname)
    ssh('www-mgr', hostname,
        '/usr/local/share/silversupport/mgr-scripts/restore-services.py %s %s'
        % (dir, config.args.location))

def move_backup_to_server(backup, hostname):
    pass
