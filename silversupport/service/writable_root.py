"""Gives a persistent location to keep files, that get served"""

from silversupport.service.files import AbstractFileService


class Service(AbstractFileService):
    root = '/var/lib/silverlining/writable-roots'
    env_var = 'CONFIG_WRITABLE_ROOT'
    home_name = 'writable-root'
