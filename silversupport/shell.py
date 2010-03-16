import os
import subprocess

def ssh(user, host, command, **kw):
    if user == 'www-data':
        # This is a bit tricky:
        user = 'www-mgr'
        command = 'sudo -H -u www-data %s' % shell_escape(command)
    ssh_args = kw.pop('ssh_args', [])
    return run(['ssh'] + ssh_args + ['-l', user, host, command], **kw)

def shell_escape(arg):
    """Escapes an argument for the shell"""
    return "'%s'" % arg.replace("'", "'\\''")

def run(command, extra_env=None, stdin=None,
        capture_stdout=False, capture_stderr=False,
        cwd=None):
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
    proc = subprocess.Popen(
        command, env=env, **kw)
    stdout, stderr = proc.communicate(stdin)
    return stdout, stderr, proc.returncode
