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

def set_etc_hosts(logger, hostname, ip):
    """Sets a line in /etc/hosts to assign the hostname to the ip

    This may add or edit to the file, or do nothing if is already set.
    It will call a subcommand with sudo if necessary to edit.
    """
    fp = open('/etc/hosts')
    try:
        for line in fp.read().splitlines():
            line = line.strip()
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split()
            line_ip = parts[0]
            line_hosts = parts[1:]
            if line_ip == ip:
                if hostname in line_hosts:
                    logger.info('Found working ip %s' % line)
                    return
            if hostname in line_hosts:
                break
    finally:
        fp.close()

    cmd = ["sudo", "python",
           os.path.join(os.path.dirname(__file__), 'update_etc_hosts.py'),
           "/etc/hosts",
           ip, hostname]
    logger.notify('The hostname/ip is not setup in /etc/hosts')
    resp = raw_input('Would you like me to set it up? ')
    resp = resp.strip().lower()
    if resp and resp[0] == 'y':
        logger.notify('Executing %s' % ' '.join(cmd))
        proc = subprocess.Popen(cmd)
        proc.communicate()
