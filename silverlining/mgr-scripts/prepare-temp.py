#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from optparse import OptionParser
from silversupport import appdata
from silversupport.shell import run

parser = OptionParser(
    usage="%prog TMP_LOCATION HOSTNAME APP_NAME",
    description="""\
Copy the application (or app instance) into the temporary location
""")
parser.add_option(
    '--instance-name',
    metavar='NAME',
    help="A specific instance name to select")

def main():
    options, args = parser.parse_args()
    tmp_location = args[0]
    hostname = args[1]
    app_name = args[2]
    instance_name = options.instance_name
    if not instance_name:
        instance_name = appdata.instance_for_app_name(hostname, app_name)
        if not instance_name:
            print 'Error: No instance can be found under http://%s with the name %r' % (
                hostname, app_name)
    location = os.path.join('/var/www', instance_name)
    run(['cp', '-arl', location, tmp_location])


if __name__ == '__main__':
    main()
