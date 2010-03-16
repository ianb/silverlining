from setuptools import setup, find_packages
import sys, os
from fnmatch import fnmatchcase
from distutils.util import convert_path

version = '0.1'

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ('*.pyc', '*~', '.*', '*.bak')
standard_exclude_directories = (
    '.*', 'CVS', '.svn', '.hg', '_darcs', './build',
    './dist', 'EGG-INFO', '*.egg-info')

def find_package_data(
    where='.', package='',
    exclude=standard_exclude,
    exclude_directories=standard_exclude_directories,
    only_in_packages=True,
    show_ignored=False,
    fake_packages=()):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {'package': [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """
    
    out = {}
    stack = [(convert_path(where), '', package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, '__init__.py'))
                    and not prefix
                    and os.path.basename(fn) not in fake_packages):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                    stack.append((fn, '', new_package, False))
                else:
                    stack.append((fn, prefix + name + '/', package, only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if (name.endswith('.py')
                    and os.path.exists(os.path.join(where, '__init__.py'))
                    and os.path.basename(where) not in fake_packages):
                    bad_name = True
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='SilverLining',
      version=version,
      description="Library for creating cloud servers",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian Bicking',
      author_email='ianb@openplans.org',
      url='',
      license='GPL',
      packages=['silverlining', 'silverlining.commands', 'silversupport'],
      zip_safe=False,
      install_requires=[
          'CmdUtils',
          'apache-libcloud',
          'Tempita',
          'argparse',
          'virtualenv>=1.4.3',
          'INITools',
          'zope.interface',
      ],
      entry_points="""
      [console_scripts]
      silver = silverlining.runner:main
      """,
      package_data=find_package_data(
          where=os.path.join(os.path.dirname(__file__), 'silverlining'),
          package='silverlining',
          fake_packages=['silverlining', 'service']),
      )
