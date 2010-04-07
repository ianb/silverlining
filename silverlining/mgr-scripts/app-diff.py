#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
import shutil
from optparse import OptionParser
from silversupport import appdata
from silversupport.shell import run
from silversupport.transfermethods import make_temp_name

parser = OptionParser(
    usage="%prog TMP_LOCATION HOSTNAME APP_NAME",
    description="""\
Diff between the files in TMP_LOCATION and the identified application.

Will delete the files in TMP_LOCATION unless --keep-tmp is given
""")
parser.add_option(
    '--instance-name',
    metavar='NAME',
    help="A specific instance name to select")
parser.add_option(
    '--keep-tmp',
    action='store_true',
    help="Keep the files in TMP_LOCATION instead of removing them after the diff")


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
    tmp = make_temp_name('.diffing')
    for magic_file in ['silver-env-variables.php']:
        if os.path.exists(os.path.join(location, magic_file)):
            shutil.copy(os.path.join(location, magic_file),
                        os.path.join(tmp_location, magic_file))
    os.mkdir(tmp)
    os.symlink(location, os.path.join(tmp, instance_name))
    os.symlink(tmp_location, os.path.join(tmp, 'local'))
    run(['diff', '-u', instance_name, 'local'],
        cwd=tmp)
    shutil.rmtree(tmp)
    if not options.keep_tmp:
        shutil.rmtree(tmp_location)


if __name__ == '__main__':
    main()
