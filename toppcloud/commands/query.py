import subprocess
import re
import fnmatch

def command_query(config):
    proc = subprocess.Popen(
        ['ssh', '%s@%s' % (config['remote_username'], config.node_hostname),
         'cat /var/www/hostmap.txt; echo "END" ; ls /var/www'],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    hosts = {}
    lines = [line.strip()
             for line in stdout.splitlines()
             if line.strip() and not line.strip().startswith('#')]
    hosts = {}
    site_instances = {}
    instance_site = {}
    sites = set()
    while 1:
        if not lines:
            break
        line = lines.pop(0)
        if line == 'END':
            break
        hostname, sitename = line.split(None, 1)
        hosts[hostname] = sitename
    for line in lines:
        match = re.match(r'^(?:([a-z0-9_.-]+)\.(\d+)\.(.*)|default-[a-z]+)$',
                         line)
        if not match:
            continue
        if not match.group(1):
            site_name = line
            version = ''
            release = ''
        else:
            site_name = match.group(1)
            version = match.group(2)
            release = match.group(3)
        site_instances.setdefault(site_name, {})[(version, release)] = line
        sites.add(site_name)
        instance_site[line] = site_name
    site_names = getattr(config.args, 'site-name')
    if site_names:
        matcher = re.compile('|'.join(fnmatch.translate(s) for s in site_names))
        new_hosts = {}
        new_site_instances = {}
        new_instance_site = {}
        new_sites = set()
        for site in sites:
            if matcher.match(site):
                new_sites.add(site)
        for hostname, instance in hosts.iteritems():
            if matcher.match(hostname):
                new_sites.add(instance.split('.')[0])
        for site in new_sites:
            new_site_instances[site] = site_instances[site]
            for n, v in instance_site.iteritems():
                if v == site:
                    new_instance_site[n] = v
            for n, v in hosts.iteritems():
                if v.startswith(site):
                    new_hosts[n] = v
        hosts = new_hosts
        site_instances = new_site_instances
        instance_site = new_instance_site
        sites = new_sites
    info = config.logger.info
    notify = config.logger.notify
    for site in sorted(sites):
        if len(sites) > 1:
            notify('Site: %s' % site)
            config.logger.indent += 2
        try:
            for (version, release), instance_name in sorted(site_instances[site].items()):
                hostnames = []
                for hostname, inst in hosts.items():
                    if ':' in hostname:
                        # boring
                        continue
                    if hostname.startswith('www.'):
                        continue
                    if inst == instance_name:
                        hostnames.append(hostname)
                if not hostnames:
                    notify('%s (defunct instance)' % instance_name)
                elif len(hostnames) == 1:
                    notify('%s: %s' % (instance_name, hostnames[0]))
                else:
                    notify('%s:' % instance_name)
                    for hostname in sorted(hostnames):
                        notify('  %s' % hostname)
        finally:
            if len(sites) > 1:
                config.logger.indent -= 2
