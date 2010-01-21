import os
import re
from cStringIO import StringIO
import zipfile
import subprocess
from cmdutils import CommandError
from toppcloud.runner import App

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
    if args.user == 'root':
        ssh_host = 'root@%s' % args.host
        cmd_prefix = ''
    elif args.user == 'www-mgr':
        ssh_host = 'www-mgr@%s' % args.host
        cmd_prefix = ''
    elif args.user == 'www-data':
        ssh_host = 'www-mgr@%s' % args.host
        cmd_prefix = 'sudo -H -u www-data '
    else:
        raise CommandError(
            "Unknown --user=%s" % args.user)
    env = os.environ.copy()
    env['LANG'] = 'C'
    if any_translated:
        proc = subprocess.Popen(
            ['ssh', ssh_host,
             '%s/var/www/support/save-tmp-file.py' % cmd_prefix],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate(zip_content)
        match = _tmp_re.search(stdout)
        if not match:
            raise CommandError(
                "Got bad output from save-tmp-file.py:\n%s" % stdout)
        location = match.group(1)
    else:
        location = 'NONE'
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '%s/var/www/support/run-command.py %s %s %s %s'
         % (cmd_prefix, args.host, location, args.script,
            shell_quoted(translated_args))],
        env=env)
    proc.communicate()
    return proc.returncode

def shell_quoted(values):
    result = []
    for value in values:
        result.append("\"'\"".join(
            "'%s'" % v
            for v in value.split("'")))
    return ' '.join(result)

    

