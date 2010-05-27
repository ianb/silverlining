"""Serve an app locally/for development"""
import os
import sys
import subprocess
from cmdutils import CommandError
from paste import httpserver


def command_serve(config):
    dir = os.path.abspath(config.args.dir)
    if not os.path.exists(os.path.join(config.args.dir, 'app.ini')):
        raise CommandError(
            "Could not find app.ini in %s" % config.args.dir)
    if os.path.exists(os.path.join(dir, 'bin', 'python')):
        # We are in a virtualenv situation...
        cmd = [os.path.join(dir, 'bin', 'python'),
               os.path.abspath(os.path.join(__file__, '../../devel-runner.py')),
               dir]
    else:
        cmd = [sys.executable,
               os.path.abspath(os.path.join(__file__, '../../devel-runner.py')),
               dir]
    ## FIXME: should cut down the environ significantly
    environ = os.environ.copy()
    environ['SILVER_INSTANCE_NAME'] = 'localhost'
    environ['SILVER_PASTE_LOCATION'] = httpserver.__file__
    environ['SILVER_SERVE_HOST'] = config.args.host
    environ['SILVER_SERVE_PORT'] = config.args.port
    proc = None
    try:
        try:
            while 1:
                proc = subprocess.Popen(cmd, cwd=dir, env=environ)
                proc.communicate()
                if proc.returncode == 3:
                    # Signal to do a restart
                    config.logger.notify('Restarting...')
                else:
                    return
            sys.exit(proc.returncode)
        finally:
            if (proc is not None
                and hasattr(os, 'kill')):
                import signal
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                except (OSError, IOError):
                    pass
    except KeyboardInterrupt:
        print 'Terminating'


def _turn_sigterm_into_systemexit():
    """
    Attempts to turn a SIGTERM exception into a SystemExit exception.
    """
    try:
        import signal
    except ImportError:
        return

    def handle_term(signo, frame):
        raise SystemExit
    signal.signal(signal.SIGTERM, handle_term)
