"""List active nodes"""


def command_list_nodes(config):
    for node in config.driver.list_nodes():
        config.logger.notify(
            '%s:%s %s' % (
                node.name, ' '*(30-len(node.name)),
                ', '.join(node.public_ip)))
