import os
import sys
import subprocess

def serve(config):
    dir = os.path.abspath(config.args.dir)
    if os.path.exists(os.path.join(dir, 'bin', 'python')):
        # We are in a virtualenv situation...
        cmd = [os.path.join(dir, 'bin', 'python'),
               os.path.join(os.path.dirname(__file__),
                            'devel-runner.py'),
               dir]
    else:
        cmd = [sys.executable,
               os.path.join(os.path.dirname(__file__),
                            'devel-runner.py'),
               dir]
    ## FIXME: should cut down the environ significantly
    environ = os.environ.copy()
    environ['SITE'] = 'localhost'
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
