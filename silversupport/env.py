"""Functions specifically related to the environment this is running in."""

import os

__all__ = ['is_production', 'local_location']


def is_production():
    """Returns true if this is a production environment.  False if it
    is development or unknown"""
    ## FIXME: this is lame.  It's causing prolbems with the CI server too.
    return os.path.exists('/usr/local/share/silverlining/lib')


def local_location(path):
    """Returns a filename for storing information locally

    Typically this is ``~/.silverlining/<path>``
    """
    assert not is_production()
    path = os.path.join(os.environ['HOME'], '.silverlining', path)
    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    return path
