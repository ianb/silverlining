from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='toppcloud',
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
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'CmdUtils',
          'libcloud',
          'Tempita',
          'argparse',
          'virtualenv',
          'INITools',
      ],
      entry_points="""
      [console_scripts]
      toppcloud = toppcloud.command:main
      """,
      )
