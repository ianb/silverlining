"""List available sizes"""


def command_list_sizes(config):
    sizes = config.driver.list_sizes()
    try:
        default_size = config.select_size(sizes=sizes)
    except LookupError:
        default_size = None
        config.logger.info('[%s] has no default size' % (
            config['section_name']))
    for size in sizes:
        if default_size and size.id == default_size.id:
            default = '**default**'
        else:
            default = ''
        config.logger.notify('%s %14s: ram=%5sMb, disk=%3sGb %s' % (
            size.id, size.name, size.ram, size.disk, default))
