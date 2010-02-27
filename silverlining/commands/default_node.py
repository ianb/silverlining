def command_default_node(config):
    default_node = config.args.node
    assert default_node
    config.set_default_node(default_node)
