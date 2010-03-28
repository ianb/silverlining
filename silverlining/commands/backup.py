"""Cleans out unused instances from a server"""
import re
from cmdutils import CommandError
from silversupport.shell import ssh, run
from silversupport.appdata import normalize_location
from silversupport import transfermethods

_backup_path_re = re.compile(r'backup="(.*?)"')
_scheme_re = re.compile(r'^[a-z]+:')
_archive_path_re = re.compile(r'archive="(.*?)"')


def command_backup(config):
    hostname, path = normalize_location(config.args.location)
    stdout, stderr, returncode = ssh(
        'www-mgr', hostname,
        '/usr/local/share/silverlining/mgr-scripts/backup-services.py %s' % config.args.location,
        capture_stdout=True)
    match = _backup_path_re.search(stdout)
    if not match:
        config.logger.fatal("Unexpected output from backup-services.py: %r" % stdout)
        raise CommandError("Bad output")
    backup_path = match.group(1)
    config.logger.notify("Backed up to %s:%s" % (hostname, backup_path))
    if not _scheme_re.search(config.args.destination):
        copy_local(hostname, backup_path, config.args.destination)
    else:
        ssh('www-mgr', hostname,
            '/usr/local/share/silverlining/mgr-scripts/transfer-backup.py %s %s'
            % (backup_path, config.args.destination))


def copy_local(hostname, backup_path, dest):
    clean_paths = [backup_path]
    if transfermethods.is_archive(dest):
        stdout, stderr, returncode = ssh(
            'www-mgr', hostname,
            '/usr/local/share/silverlining/mgr-scripts/transfer-backup.py --archive %s %s'
            % (backup_path, transfermethods.extension(dest)),
            capture_stdout=True)
        match = _archive_path_re.search(stdout)
        if not match:
            raise CommandError("Bad output from transfer-backup.py: %r" % stdout)
        backup_path = match.group(1)
        clean_paths.append(backup_path)
    stdout, stderr, returncode = run(['scp', '-r', 'www-mgr@%s:%s' % (hostname, backup_path), dest])
    if returncode:
        raise CommandError("Error copying locally (scp exited with code %s); %s remains on server"
                           % (returncode, ' '.join(clean_paths)))
    ssh('www-mgr', hostname, 'rm -r %s' % ' '.join(clean_paths))
