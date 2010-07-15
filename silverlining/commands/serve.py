"""Serve an app locally/for development"""
import os
import sys
import subprocess
import glob
import tempfile
from cmdutils import CommandError
from tempita import Template
from paste import httpserver
import silversupport
from silversupport.appconfig import AppConfig
from silversupport.shell import run


def command_serve(config):
    dir = os.path.abspath(config.args.dir)
    if not os.path.exists(os.path.join(dir, 'app.ini')):
        raise CommandError(
            "Could not find app.ini in %s" % config.args.dir)
    appconfig = AppConfig(os.path.join(dir, 'app.ini'))
    appconfig.check_service_setup(config.logger)
    if appconfig.platform == 'python':
        serve_python(config, appconfig)
    elif appconfig.platform == 'php':
        serve_php(config, appconfig)


def serve_python(config, appconfig):
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
    if config.args.config:
        environ['SILVER_APP_CONFIG'] = os.path.abspath(config.args.config)
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


def serve_php(config, appconfig):
    apache_config_tmpl = Template.from_filename(
        os.path.join(os.path.dirname(__file__), 'php-devel-server.conf.tmpl'))
    path_prefixes = ['./static', appconfig.php_root]
    if appconfig.writable_root_location:
        path_prefixes.append(appconfig.writable_root_location
                             + '/%{ENV:SILVER_HOSTNAME}')
        path_prefixes.append(appconfig.writable_root_location)
    tempdir = os.path.join(config.args.dir, '.apache')
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    includes = glob.glob('/etc/apache2/mods-enabled/*.load')
    includes += glob.glob('/etc/apache2/mods-enabled/*.conf')
    silver_secret_file = os.path.join(tempdir, 'secret.txt')
    silver_env_vars = os.path.join(tempdir, 'silver-env-vars.php')
    appconfig.write_php_env(silver_env_vars)
    if not os.path.exists(silver_secret_file):
        fp = open(silver_secret_file, 'wb')
        fp.write('localsecret')
        fp.close()
    apache_config = apache_config_tmpl.substitute(
        mgr_scripts=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mgr-scripts'),
        path_prefixes=path_prefixes,
        ## FIXME: better values:
        tempdir=tempdir,
        apache_pid_file=os.path.join(tempdir, 'apache.pid'),
        mods_dir='/etc/apache2/mods-enabled',
        includes=includes,
        silver_instance_dir=os.path.abspath(config.args.dir),
        silver_secret_file=silver_secret_file,
        silver_env_vars=silver_env_vars,
        silver_funcs=os.path.join(os.path.dirname(silversupport.__file__), 'php', 'functions.php'),
        )
    conf_file = os.path.join(tempdir, 'apache.conf')
    config.logger.info('Writing config to %s' % conf_file)
    fp = open(conf_file, 'w')
    fp.write(apache_config)
    fp.close()
    exe_name = search_path(['apache2', 'apache', 'httpd'])
    config.logger.notify('Serving on http://localhost:8080')
    run([exe_name, '-f', conf_file,
         '-d', config.args.dir, '-X'])
    

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


def search_path(exe_names):
    ## FIXME: should I allow for some general environmental variable override here?
    paths = os.environ['PATH'].split(os.path.pathsep)
    for name in exe_names:
        for path in paths:
            if os.path.exists(os.path.join(path, name)):
                return name
    return exe_names[0]
