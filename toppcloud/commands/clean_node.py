import subprocess

def command_clean_node(config):
    ssh_host = '%s@%s' % (config['remote_username'],
                          config.node_hostname)
    if config.args.simulate:
        simulate = '-n'
    else:
        simulate = ''
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/cleanup-apps.py %s' % simulate])
    proc.communicate()
