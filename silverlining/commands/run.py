"""Run a remote command"""
import os
import re
from cStringIO import StringIO
import zipfile
from cmdutils import CommandError
from silversupport.shell import ssh, shell_escape

_tmp_re = re.compile(r'tmp="(.*)"')


def command_run(config):
    args = config.args
    out = StringIO()
    zip = zipfile.ZipFile(out, 'w')
    translated_args = []
    any_translated = False
    for arg in args.unknown_args:
        if '=' in arg:
            option, filename = arg.split('=', 1)
        else:
            option = None
            filename = arg
        if os.path.exists(filename):
            if os.path.isdir(filename):
                for dirpath, dirnames, filenames in os.walk(filename):
                    relpath = dirpath.replace('\\', '/')
                    relpath = relpath[len(filename):].lstrip('/')
                    for fn in filenames:
                        zip.write(
                            os.path.join(dirpath, fn),
                            os.path.join(os.path.basename(filename), relpath, fn))
            else:
                ## FIXME: this basename might be unique
                zip.write(filename, os.path.basename(filename))
            translated_filename = os.path.join('$TMP', os.path.basename(filename))
            any_translated = True
            if option:
                translated_args.append(option + translated_filename)
            else:
                translated_args.append(translated_filename)
        else:
            translated_args.append(arg)
    zip.close()
    zip_content = out.getvalue()
    if args.user not in ['root', 'www-mgr', 'www-data']:
        raise CommandError(
            "Unknown --user=%s" % args.user)
    if any_translated:
        stdout, stderr, returncode = ssh(
            args.user, args.host, '/usr/local/share/silverlining/mgr-scripts/save-tmp-file.py',
            stdin=zip_content, capture_stdout=True, capture_stderr=True)
        match = _tmp_re.search(stdout)
        if not match:
            raise CommandError(
                "Got bad output from save-tmp-file.py:\n%s" % stdout)
        location = match.group(1)
    else:
        location = 'NONE'
    stdout, stderr, returncode = ssh(
        args.user, args.host,
        '/usr/local/share/silverlining/mgr-scripts/run-command.py %s %s %s %s' %
        (args.host, location, args.script, shell_escape(translated_args)))
    return returncode
