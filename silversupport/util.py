import os

__all__ = ['unique_name']


def unique_name(dest_dir, name):
    n = 0
    result = name
    while 1:
        dest = os.path.join(dest_dir, result)
        if not os.path.exists(dest):
            return dest
        n += 1
        result = '%s_%03i' % (name, n)
