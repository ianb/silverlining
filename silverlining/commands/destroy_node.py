"""Destroy a server/node"""


def command_destroy_node(config):
    ## FIXME: This doesn't work at all, wtf?
    for node_hostname in config.args.nodes:
        ## FIXME: should update /etc/hosts
        for node in config.driver.list_nodes():
            if node.name == node_hostname:
                config.logger.notify('Destroying node %s' % node.name)
                node.destroy()
                break
        else:
            config.logger.warn('No node found with the name %s' %
                               node_hostname)
