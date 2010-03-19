#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
from silversupport.appdata import add_appdata
from optparse import OptionParser

parser = OptionParser(
    usage="%prog INSTANCE_NAME LOCATION1 LOCATION2 ...",
    description="""\
Updates /var/www/appdata.map
This sets the new hostname(s) (HOSTNAME1 etc) to point to INSTANCE_NAME.
Also the app.ini is read to write other metadata that Apache reads.
""")

parser.add_option(
    '--debug-single-process',
    action='store_true',
    help="Deploy the app as a single-process threaded app for debugging")

if __name__ == '__main__':
    options, args = parser.parse_args()
    instance_name = args[0]
    add_appdata(instance_name, args[1:], debug_single_process=options.debug_single_process)
