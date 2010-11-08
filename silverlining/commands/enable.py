from silverlining.commands import disable


def command_enable(config):
    return disable.command_disable(config, enable=True)
