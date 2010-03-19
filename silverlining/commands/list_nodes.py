"""List active nodes"""
from cmdutils import CommandError


def command_list_nodes(config):
    try:
        default_node_name = config.node_hostname
    except CommandError:
        default_node_name = None
    for node in config.driver.list_nodes():
        if node.name == default_node_name:
            default = '** default **'
        else:
            default = ''
        config.logger.notify(
            '%s:%s %6s  %15s %s' % (
                node.name, ' '*(22-len(node.name)), node.state,
                ', '.join(node.public_ip), default))
