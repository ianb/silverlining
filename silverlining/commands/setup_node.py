import os
from cmdutils import CommandError
from silversupport.shell import ssh, run

def setup_rsync(config, source, dest):
    cwd = os.path.abspath(os.path.join(__file__, '../..'))
    stdout, stderr, returncode = run([
        'rsync', '--quiet', '-prvC',
        source, 'root@%s:%s' % (config.args.node, dest)],
                                     cwd=cwd)
    config.logger.notify(
        "rsyncing %s to %s" % (source, dest))
    if returncode:
        config.logger.fatal(
            "An error occurred in rsync (code=%s)" % returncode)
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
    ssh('root', node, '''
if [ -e /root/.silverlining-server-setup ] ; then
    exit 50
fi
mkdir -p /usr/local/share/silverlining/lib
mkdir -p /root/.ssh
cat >> /root/.ssh/authorized_keys
''',
        ssh_args=['-o', 'StrictHostKeyChecking=no'],
        stdin=key)
    config.logger.notify(
        "Updating indexes and setting up rsync")
    stdout, stderr, returncode = ssh(
        'root', node, '''
dpkg --configure -a
apt-get update -qq
apt-get -y -q install rsync
''')
    if returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 3
    config.logger.notify(
        "Running apt-get install on server")
    lines = list(open(os.path.abspath(
        os.path.join(__file__, '../../server-sync-scripts/dpkg-query.txt'))))
    packages = ' '.join(line.strip().split()[0]
                        for line in lines
                        if line.strip())
    stdout, stderr, returncode = ssh(
        'root', node, 'apt-get -y -q=2 install $(cat)',
        stdin=packages)
    if returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % returncode)
        response = config.ask(
            "Continue?")
        if not response:
            return 5
    
    setup_rsync(config, 'server-root/', '/')
    setup_rsync(config,
                os.path.abspath(os.path.join(__file__, '../../../silversupport/'))+'/',
                '/usr/local/share/silverlining/lib/silversupport/')
    setup_rsync(config,
                os.path.abspath(os.path.join(__file__, '../../mgr-scripts/'))+'/',
                '/usr/local/share/silverlining/mgr-scripts/')
    ssh('root', node, 'mv /var/root/* /root/')
    
    # Move over the root files, we do *not* rsync a /root dir because
    # that would copy the wrong permissions for the /root directorty
    # which results in ssh key auth no longer working
    
    
    setup_script = open(os.path.abspath(os.path.join(
        __file__, '../../server-sync-scripts/update-server-script.sh'))).read()
    import getpass
    username = getpass.getuser()
    setup_script = setup_script.replace('__REMOTE_USER__', username)

    stdout, stderr, returncode = ssh(
        'root', node, setup_script)
    if returncode:
        config.logger.fatal(
            "An error occurred (code=%r)"
            % returncode)
        # No need to ask because it's the last task anyway
        return 6
