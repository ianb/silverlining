"""Gives a persistent location to keep files, that get served"""

from silversupport.service.files import FileService

service = FileService(
    '/var/lib/silverlining/writable-roots', 'CONFIG_WRITABLE_ROOT', 'writable-root')
install = service.install
app_setup = service.app_setup
backup = service.backup
restore = service.restore
clear = service.clear
