import os
import subprocess

__all__ = ['get_host_ip', 'set_etc_hosts']


def get_host_ip(hostname):
    """Get the IP for a given hostname, looking (only) in /etc/hosts"""
    ## FIXME: this should use DNS, or at least try DNS
    fp = open('/etc/hosts')
    try:
        for line in fp:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            ip, hostnames = line.split(None, 1)
            hostnames = hostnames.split()
            if hostname in hostnames:
                return ip
        raise Exception("Could not find hostname %s in /etc/hosts"
                        % hostname)
    finally:
        fp.close()

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
        proc = subprocess.Popen(cmd)
        proc.communicate()
