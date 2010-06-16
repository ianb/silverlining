"""Handle /etc/hosts

This has methods to put a new host->ip setting in /etc/hosts, as well
as get a setting from that file.

As /etc/hosts can only be edited by root, this ultimately calls out to
sudo to do the actual edit.
"""

import os
from silversupport.shell import run

__all__ = ['set_etc_hosts']

def set_etc_hosts(config, hostnames, ip):
    """Sets a line in /etc/hosts to assign the hostname to the ip

    This may add or edit to the file, or do nothing if is already set.
    It will call a subcommand with sudo if necessary to edit.
    """
    assert not isinstance(hostnames, basestring)
    fp = open('/etc/hosts')
    hostnames = set(hostnames)
    try:
        for line in fp.read().splitlines():
            line = line.strip()
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split()
            line_ip = parts[0]
            line_hosts = parts[1:]
            if line_ip == ip:
                for hostname in list(hostnames):
                    if hostname in line_hosts:
                        config.logger.info('Found working ip %s' % line)
                        hostnames.remove(hostname)
                        return
            force_update = False
            for hostname in hostnames:
                if hostname in line_hosts:
                    force_update = True
                    break
            if force_update:
                break
    finally:
        fp.close()

    cmd = ["sudo", "python",
           os.path.join(os.path.dirname(__file__), 'update_etc_hosts.py'),
           "/etc/hosts",
           ip] + list(hostnames)
    config.logger.notify('The hostname/ip is not setup in /etc/hosts')
    resp = config.ask('Would you like me to set it up? ')
    if resp:
        config.logger.notify('Executing %s' % ' '.join(cmd))
        run(cmd)
