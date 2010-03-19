import re
import time
from cmdutils import CommandError
from silverlining.etchosts import set_etc_hosts
from silversupport.shell import run

ESTIMATED_TIME = 60
AFTER_PING_WAIT = 10

def command_create_node(config):
    config.logger.info('Getting image/size info')
    image = config.select_image(image_id=config.args.image_id)
    size = config.select_size(size_id=config.args.size_id)
    config.logger.notify('Creating node (image=%s; size=%s)' % (
        image.name, size.name))
    node_hostname = config.node_hostname
    if not re.search(r'^[a-z0-9.-]+$', node_hostname):
        raise CommandError(
            "Invalid hostname (must contain only letters, numbers, ., and -): %r"
            % node_hostname)
    assert node_hostname
    resp = config.driver.create_node(
        name=node_hostname,
        image=image,
        size=size,
        files={'/root/.ssh/authorized_keys2': config.get('root_authorized_keys')},
        )
    public_ip = resp.public_ip[0]
    config.logger.notify('Status %s at IP %s' % (
        resp.state, public_ip))
    set_etc_hosts(config, [node_hostname], public_ip)

    if config.args.setup_node or config.args.wait:
        wait_for_node_ready_ping(config, public_ip)
        config.logger.notify('Waiting %s seconds for full boot'
                             % AFTER_PING_WAIT)
        time.sleep(AFTER_PING_WAIT)
        if config.args.setup_node:
            from silverlining.commands.setup_node import command_setup_node
            config.args.node = node_hostname
            config.logger.notify('Setting up server')
            command_setup_node(config)
       
def wait_for_node_ready(config, node_name):
    config.logger.start_progress('Waiting for server to be ready...')
    config.logger.debug('Waiting an initial %s seconds' % ESTIMATED_TIME)
    time.sleep(ESTIMATED_TIME)
    while 1:
        config.logger.show_progress()
        for node in config.driver.list_nodes():
            if node.name == node_name:
                if node.state == 'ACTIVE':
                    active = True
                else:
                    active = False
                break
        else:
            config.logger.warn(
                "No node with the name %s listed" % node_name)
            config.logger.warn(
                "Continuing, but this may not complete")
        time.sleep(10)
    config.logger.end_progress('server active.')

def wait_for_node_ready_ping(config, node_hostname):
    start = time.time()
    config.logger.start_progress('Waiting for server to be ready...')
    config.logger.debug('Waiting an initial %s seconds' % ESTIMATED_TIME)
    time.sleep(ESTIMATED_TIME)
    while 1:
        config.logger.show_progress()
        stdout, stderr, returncode = run(
            ['ping', '-c 2', '-w', '10', node_hostname],
            capture_stdout=True, capture_stderr=True)
        if returncode:
            config.logger.debug('Ping did not return successful result')
        else:
            config.logger.end_progress(
                "Server created (%s to create)" % format_time(time.time()-start))
            break

def format_time(secs):
    return '%i:%02i' % (int(secs/60), int(secs)%60)

