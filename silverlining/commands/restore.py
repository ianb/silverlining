"""Cleans out unused instances from a server"""
import os
import time
from silversupport.shell import ssh, run
from silversupport.appdata import normalize_location
from silversupport import transfermethods


def command_restore(config):
    backup = config.args.backup
    hostname, path = normalize_location(config.args.location)
    dir = move_to_server(backup, hostname)
    ssh('www-mgr', hostname,
        '/usr/local/share/silverlining/mgr-scripts/restore-services.py %s %s'
        % (dir, config.args.location))


def move_to_server(backup, hostname):
    if os.path.exists(backup):
        if not transfermethods.is_archive(backup):
            fn = transfermethods.make_temp_name('test.tar.gz')
            backup = os.path.abspath(backup)
            run(['tar', 'fcz', fn, os.path.basename(backup)],
                cwd=os.path.dirname(backup))
        else:
            fn = backup
        dest_path = '/tmp/%s-%s-%s' % (os.getpid(), int(time.time()), os.path.basename(backup))
        try:
            run(['scp', '-r', backup, 'www-mgr@%s:%s' % (hostname, dest_path)])
        finally:
            if fn != backup:
                os.unlink(fn)
        return dest_path
    if backup.startswith('remote:'):
        dest_path = '/tmp/%s-%s' % (os.getpid(), time.time())
        if transfermethods.is_archive(backup):
            dest_path += os.path.splitext(backup)[1]
        ssh('www-mgr', hostname,
            ['cp', '-ar', backup[len('remote:')], dest_path])
        return dest_path
    if backup.startswith('site:'):
        raise NotImplementedError('site: has not yet been implemented')
    if backup.startswith('ssh:'):
        backup = backup[len('ssh:'):].lstrip('/')
        backup_hostname, path = backup.split('/', 1)
        dest = '/tmp/%s-%s' % (os.getpid(), time.time())
        ssh('www-mgr',
            hostname,
            'scp -r %s:%s %s' % (backup_hostname, path, dest))
        return dest
    if backup.startswith('rsync:'):
        backup = backup[len('rsync:'):]
        dest = '/tmp/%s-%s' % (os.getpid(), time.time())
        ssh('www-mgr',
            hostname,
            'rsync -r %s %s' % backup, dest)
        return dest
    else:
        assert 0, "Unknown backup location: %r" % backup
