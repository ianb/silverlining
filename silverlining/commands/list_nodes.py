"""List active nodes"""


def command_list_nodes(config):
    for node in config.driver.list_nodes():
        config.logger.notify(
            '%s:%s %6s  %15s' % (
                node.name, ' '*(22-len(node.name)), node.state,
                ', '.join(node.public_ip)))
