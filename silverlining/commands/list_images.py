"""List available images"""


def command_list_images(config):
    images = config.cached_images(expiration=0)
    try:
        default_image = config.select_image(images=images)
    except LookupError:
        default_image = None
    if not default_image:
        config.logger.info(
            '[%s] has no default image' % (
                config['section_name']))
    for image in images:
        if image is default_image:
            default = '**default**'
        else:
            default = ''
        config.logger.notify('%6s %s %s' % (image.id, image.name, default))
