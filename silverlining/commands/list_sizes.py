"""List available sizes"""


def command_list_sizes(config):
    sizes = config.driver.list_sizes()
    try:
        default_size = config.select_size(sizes)
    except LookupError:
        default_size = None
        config.logger.info('[%s] has no size_id (default size)' % (
            config['section_name']))
    for size in sizes:
        if size.id == default_size:
            default = '**default**'
        else:
            default = ''
        config.logger.notify('%s %14s: ram=%5sMb, disk=%3sGb %s' % (
            size.id, size.name, size.ram, size.disk, default))
