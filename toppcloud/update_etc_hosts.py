"""Script to update /etc/hosts"""
import time

def update_hosts(filename, ip, hostname):
    fp = open(filename)
    lines = list(fp)
    fp.close()
    new_lines = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        line_ip, hostnames = line.strip().split(None, 1)
        hostnames = hostnames.split()
        if hostname in hostnames:
            if line_ip == ip:
                # Everything is okay... (odd)
                return
            # Oh no, we have to kill that!
            hostnames = hostnames.remove(hostname)
            if hostnames:
                new_lines.append('%s %s' % (line_ip, ' '.join(hostnames)))
            else:
                if new_lines and new_lines[-1].startswith('# Rackspace'):
                    new_lines.pop()
        else:
            new_lines.append(line)
    new_lines.append('# Rackspace alias set at %s:\n'
                     % time.strftime('%c'))
    new_lines.append('%s %s\n' % (ip, hostname))
    fp = open(filename, 'w')
    fp.writelines(new_lines)
    fp.close()

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    ip = sys.argv[2]
    hostnames = sys.argv[3:]
    for hostname in hostnames:
        update_hosts(filename, ip, hostname)
    
