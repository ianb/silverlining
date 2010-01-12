import re
from toppcloud import renderscripts
from cmdutils import CommandError
from toppcloud.etchosts import set_etc_hosts

def command_create_node(config):
    config.logger.info('Getting image/size info')
    image = config.select_image(image_id=config.args.image_id)
    size = config.select_size(size_id=config.args.size_id)
    files = renderscripts.render_files(config=config)
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
        files=files,
        )
    public_ip = resp.public_ip[0]
    config.logger.notify('Status %s at IP %s' % (
        resp.state, public_ip))
    set_etc_hosts(config, [node_hostname], public_ip)
