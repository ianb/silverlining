"""Functions specifically related to the environment this is running in."""

import os

__all__ = ['is_production']


def is_production():
    """Returns true if this is a production environment.  False if it
    is development or unknown"""
    return os.environ.get('SILVER_VERSION', '').startswith('silverlining/')
