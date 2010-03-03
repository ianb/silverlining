import os
import subprocess
from cmdutils import CommandError

def setup_rsync(config, source, dest):
    cwd = os.path.abspath(os.path.join(__file__, '../../server-files'))
    proc = subprocess.Popen([
        'rsync', '--quiet', '-prvC',
        source, 'root@%s:%s' % (config.args.node, dest)],
                            cwd=cwd)
    config.logger.notify(
        "rsyncing %s to %s" % (source, dest))
    proc.communicate()
    if proc.returncode:
        config.logger.fatal(
            "An error occurred in rsync (code=%s)" % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            raise CommandError(
                "Aborting due to failure")

def command_setup_node(config):
    os.environ['LANG'] = 'C'
    node = config.args.node
    config.logger.notify(
        'Setting up authentication on server...')
    ssh_host = 'root@%s' % node
    proc = subprocess.Popen([
        'ssh', '-o', 'StrictHostKeyChecking=no',
        ssh_host, '''
if [ -e /root/.silverlining-server-setup ] ; then
    exit 50
fi
mkdir -p /root/.ssh
cat >> /root/.ssh/authorized_keys
''',
        ], stdin=subprocess.PIPE)
    for path in ['id_rsa.pub', 'id_dsa.pub']:
        pubkey_path = os.path.join(os.environ['HOME'], '.ssh', path)
        if os.path.exists(pubkey_path):
            key = open(pubkey_path, 'rb').read()
            config.logger.notify("Using key file:  %s", pubkey_path)
            break
    else:
        config.logger.fatal("Can't locate any key file")
        #not sure what error code are used for here but 8 was unused
        return 8
    proc.communicate(key)
    # if proc.returncode == 50:
    #     config.logger.fatal(
    #         "The server has already been setup (/root/.silverlining-server-setup exists)")
    #     return 2
    config.logger.notify(
        "Updating indexes and setting up rsync")
    proc = subprocess.Popen([
        'ssh', ssh_host, '''
apt-get update -qq
apt-get -y -q install rsync
''',
        ])
    proc.communicate()
    if proc.returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 3
    config.logger.notify(
        "Running apt-get install on server")
    lines = list(open(os.path.abspath(
        os.path.join(__file__, '../../server-files/dpkg-query.txt'))))
    packages = ' '.join(line.strip().split()[0]
                        for line in lines
                        if line.strip())
    proc = subprocess.Popen([
        'ssh', ssh_host,
        'apt-get -y -q=2 install $(cat)'],
                            stdin=subprocess.PIPE)
    proc.communicate(packages)
    if proc.returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % proc.returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 5
    
    setup_rsync(config, 'serverroot/', '/')
    proc = subprocess.Popen([
        'ssh', ssh_host,
        'mv /var/root/* /root/'])
    proc.communicate()
    
    # Move over the root files, we do *not* rsync a /root dir because
    # that would copy the wrong permissions for the /root directorty
    # which results in ssh key auth no longer working
    
    
    setup_script = open(os.path.abspath(os.path.join(
        __file__, '../../server-files/update-server-script.sh'))).read()
    import getpass
    username = getpass.getuser()
    setup_script = setup_script.replace('__REMOTE_USER__', username)
    
    stdout, returncode = config.run(
        ['ssh', ssh_host, setup_script])
    if returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % returncode)
        # No need to ask because it's the last task anyway
        return 6