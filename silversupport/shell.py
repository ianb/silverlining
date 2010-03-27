"""Simple shell routines"""

import os
import re
import subprocess

__all__ = ['ssh', 'run', 'apt_install', 'shell_escape',
           'conditional_shell_escape']


def ssh(user, host, command, **kw):
    """Runs ssh to the given user/host, and runs the command.

    Any extra keyword arguments are passed to ``run``.

    This will use sudo for some users, and ssh in directory in other cases.
    """
    if isinstance(command, (list, tuple)):
        command = ' '.join(conditional_shell_escape(i) for i in command)
    if user == 'www-data':
        # This is a bit tricky:
        user = 'www-mgr'
        command = 'sudo -H -u www-data %s' % shell_escape(command)
    ssh_args = kw.pop('ssh_args', [])
    return run(['ssh'] + ssh_args + ['-l', user, host, command], **kw)


def run(command, extra_env=None, stdin=None,
        capture_stdout=False, capture_stderr=False,
        cwd=None):
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
    return stdout, stderr, proc.returncode


def apt_install(packages, **kw):
    """Install the given list of packages"""
    return run(['apt-get', 'install', '-q=2', '-y', '--force-yes'] + packages, **kw)


def shell_escape(arg):
    """Escapes an argument for the shell"""
    return "'%s'" % arg.replace("'", "'\\''")


def conditional_shell_escape(arg):
    """Escapes an argument, unless it's obvious it doesn't need
    escaping"""
    if re.match(r'^[a-zA-Z0-9_,./-]+$', arg):
        return arg
    else:
        return shell_escape(arg)
