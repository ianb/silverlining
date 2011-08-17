"""Simple shell routines"""

import os
import re
import subprocess

__all__ = ['ssh', 'run', 'apt_install', 'shell_escape',
           'conditional_shell_escape', 'overwrite_file',
           'add_to_file']


def ssh(user, host, command, **kw):
    """Runs ssh to the given user/host, and runs the command.

    Any extra keyword arguments are passed to ``run``.

    This will use sudo for some users, and ssh in directory in other cases.
    """
    if user == 'www-data':
        # This is a bit tricky:
        user = 'www-mgr'
        if isinstance(command, (list, tuple)):
            command = ' '.join(conditional_shell_escape(i) for i in command)
        else:
            command = conditional_shell_escape(command)
        command = 'sudo -H -u www-data %s' % command
    elif isinstance(command, (list, tuple)):
        command = ' '.join(conditional_shell_escape(i) for i in command)
    ssh_args = list(kw.pop('ssh_args', []))
    strict_host_key_checking = kw.pop('strict_host_key_checking', False)
    if not strict_host_key_checking:
        ssh_args.extend(['-o', 'StrictHostKeyChecking=no'])
    return run(['ssh'] + ssh_args + ['-l', user, host, command], **kw)


def run(command, extra_env=None, stdin=None,
        capture_stdout=False, capture_stderr=False,
        cwd=None, fail_on_error=False):
    """Runs a command.

    The command may be a string or (preferred) a list of
    command+arguments.  extra_env is extra environmental keys to set.
    stdin is a string to pass in.  You can capture stdout and/or
    stderr; if you do not they are streamed directly.  Similarly if
    you do not give stdin, then the command is attached to the regular
    stdin.

    This always return ``(stdout, stderr, returncode)``.  The first
    two may be None if you didn't capture them.
    """
    env = os.environ.copy()
    env['LANG'] = 'C'
    if extra_env:
        env.update(extra_env)
    kw = {}
    if stdin:
        kw['stdin'] = subprocess.PIPE
    if capture_stdout:
        kw['stdout'] = subprocess.PIPE
    if capture_stderr:
        kw['stderr'] = subprocess.PIPE
    if cwd:
        kw['cwd'] = cwd
    for key, value in env.items():
        assert isinstance(value, str), "bad value %r: %r" % (key, value)
    for v in command:
        assert isinstance(v, str), "bad command argument %r" % v
    try:
        proc = subprocess.Popen(
            command, env=env, **kw)
    except OSError, e:
        raise OSError('Error while running command "%s": %s' % (
            ' '.join(conditional_shell_escape(i) for i in command), e))
    stdout, stderr = proc.communicate(stdin or '')
    if fail_on_error and proc.returncode:
        if stderr:
            msg = '; stderr:\n%s' % stderr
        else:
            msg = ''
        raise OSError(
            'Error while running command "%s": returncode %s%s'
            % (' '.join(conditional_shell_escape(i) for i in command),
               proc.returncode, msg))
    return stdout, stderr, proc.returncode


def apt_install(packages, **kw):
    """Install the given list of packages"""
    return run(['apt-get', 'install', '-q=2', '-y', '--force-yes',
                '--no-install-recommends'] + packages, **kw)


_end_quote_re = re.compile(r"^('*)(.*?)('*)$", re.S)
_quote_re = re.compile("'+")


def shell_escape(arg):
    """Escapes an argument for the shell"""
    end_quotes_match = _end_quote_re.match(arg)
    inner = end_quotes_match.group(2)
    inner = _quote_re.sub(lambda m: "'%s'" % m.group(0).replace("'", "\\'"),
                          inner)
    return ("'" + end_quotes_match.group(1).replace("'", "\\'")
            + inner + end_quotes_match.group(3).replace("'", "\\'") + "'")


def conditional_shell_escape(arg):
    """Escapes an argument, unless it's obvious it doesn't need
    escaping"""
    if re.match(r'^[a-zA-Z0-9_,./-]+$', arg):
        return arg
    else:
        return shell_escape(arg)


def overwrite_file(dest, source_text=None, source_file=None):
    """Overwrite a file on the system"""
    if source_file:
        assert not source_text
        fp = open(source_file, 'rb')
        source_text = fp.read()
        fp.close()
    if os.path.exists(dest):
        fp = open(dest, 'rb')
        cur_text = fp.read()
        fp.close()
        if cur_text == source_text:
            return
        new = open(dest+'.silver-back', 'wb')
        new.write(cur_text)
        new.close()
    ## FIXME: is writing over the file sufficient to keep its permissions?
    fp = open(dest, 'wb')
    fp.write(source_text)
    fp.close()


def add_to_file(dest, source_text, add_newline=True):
    """Write the text to the end of the dest, or do nothing if the text
    is found in the file already (anywhere in the file)"""
    fp = open(dest, 'rb')
    content = fp.read()
    fp.close()
    if source_text in content:
        return
    if not content.endswith('\n') and add_newline:
        content += '\n'
    content += source_text
    fp = open(dest, 'wb')
    fp.write(content)
    fp.close()
