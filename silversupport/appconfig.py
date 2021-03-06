"""Application configuration object"""

import os
import pwd
import sys
import warnings
from site import addsitedir
from silversupport.env import is_production
from silversupport.shell import run
from silversupport.util import asbool, read_config
from silversupport.disabledapps import DisabledSite, is_disabled

__all__ = ['AppConfig']

DEPLOYMENT_LOCATION = "/var/www"


class AppConfig(object):
    """This represents an application's configuration file, and by
    extension represents the application itself"""

    def __init__(self, config_file, app_name=None,
                 local_config=None):
        if not os.path.exists(config_file):
            raise OSError("No config file %s" % config_file)
        self.config_file = config_file
        self.config = read_config(config_file)
        if not is_production():
            if self.config['production'].get('version'):
                warnings.warn('version setting in %s is deprecated' % config_file)
            if self.config['production'].get('default_hostname'):
                warnings.warn('default_hostname setting in %s has been renamed to default_location'
                              % config_file)
            if self.config['production'].get('default_host'):
                warnings.warn('default_host setting in %s has been renamed to default_location'
                              % config_file)
        if app_name is None:
            if is_production():
                app_name = os.path.basename(os.path.dirname(config_file)).split('.')[0]
            else:
                app_name = self.config['production']['app_name']
        self.app_name = app_name
        self.local_config = local_config

    @classmethod
    def from_instance_name(cls, instance_name):
        """Loads an instance given its name; only valid in production"""
        return cls(os.path.join(DEPLOYMENT_LOCATION, instance_name, 'app.ini'))

    @classmethod
    def from_location(cls, location):
        """Loads an instance given its location (hostname[/path])"""
        import appdata
        return cls.from_instance_name(
            appdata.instance_for_location(*appdata.normalize_location(location)))

    @property
    def platform(self):
        """The platform of the application.

        Current valid values are ``'python'`` and ``'php'``
        """
        return self.config['production'].get('platform', 'python')

    @property
    def runner(self):
        """The filename of the runner for this application"""
        filename = self.config['production']['runner']
        return os.path.join(os.path.dirname(self.config_file), filename)

    @property
    def update_fetch(self):
        """A list (possibly empty) of all URLs to fetch on update"""
        places = self.config['production'].get('update_fetch')
        if not places:
            return []
        return self._parse_lines(places)

    @property
    def default_location(self):
        """The default location to upload this application to"""
        return self.config['production'].get('default_location')

    @property
    def services(self):
        """A dictionary of configured services (keys=service name,
        value=any configuration)"""
        services = {}
        c = self.config['production']
        devel = not is_production()
        if devel:
            devel_config = self.load_devel_config()
        else:
            devel_config = None
        for name, config_string in c.items():
            if name.startswith('service.'):
                name = name[len('service.'):]
                mod = self.load_service_module(name)
                service = mod.Service(self, config_string, devel=devel,
                                      devel_config=devel_config)
                service.name = name
                services[name] = service
        return services

    def load_devel_config(self):
        from silversupport.develconfig import load_devel_config
        return load_devel_config(self.app_name)

    @property
    def service_list(self):
        return [s for n, s in sorted(self.services.items())]

    @property
    def php_root(self):
        """The php_root location (or ``/dev/null`` if none given)"""
        return os.path.join(
            self.app_dir,
            self.config['production'].get('php_root', '/dev/null'))

    @property
    def writable_root_location(self):
        """The writable-root location, if it is available.

        If not configured, ``/dev/null`` in production and ``''`` in
        development
        """
        if 'service.writable_root' in self.config['production']:
            ## FIXME: do development too
            return os.path.join('/var/lib/silverlining/writable-roots', self.app_name)
        else:
            if is_production():
                return '/dev/null'
            else:
                return ''

    @property
    def app_dir(self):
        """The directory the application lives in"""
        return os.path.dirname(self.config_file)

    @property
    def static_dir(self):
        """The location of static files"""
        return os.path.join(self.app_dir, 'static')

    @property
    def instance_name(self):
        """The name of the instance (APP_NAME.TIMESTAMP)"""
        return os.path.basename(os.path.dirname(self.config_file))

    @property
    def packages(self):
        """A list of packages that should be installed for this application"""
        return self._parse_lines(self.config['production'].get('packages'))

    @property
    def package_install_script(self):
        """A list of scripts to call to install package stuff like apt
        repositories"""
        return self._parse_lines(
            self.config['production'].get('package_install_script'),
            relative_to=self.app_dir)

    @property
    def after_install_script(self):
        """A list of scripts to call after installing packages"""
        return self._parse_lines(
            self.config['production'].get('after_install_script'),
            relative_to=self.app_dir)

    @property
    def config_required(self):
        return asbool(self.config['production'].get('config.required'))

    @property
    def config_template(self):
        tmpl = self.config['production'].get('config.template')
        if not tmpl:
            return None
        return os.path.join(self.app_dir, tmpl)

    @property
    def config_checker(self):
        obj_name = self.config['production'].get('config.checker')
        if not obj_name:
            return None
        if ':' not in obj_name:
            raise ValueError('Bad value for config.checker (%r): should be module:obj' % obj_name)
        mod_name, attrs = obj_name.split(':', 1)
        __import__(mod_name)
        mod = sys.modules[mod_name]
        obj = mod
        for attr in attrs.split('.'):
            obj = getattr(obj, attr)
        return obj

    def check_config(self, config_dir):
        checker = self.config_checker
        if not checker:
            return
        checker(config_dir)

    @property
    def config_default(self):
        dir = self.config['production'].get('config.default')
        if not dir:
            return None
        return os.path.join(self.app_dir, dir)

    def _parse_lines(self, lines, relative_to=None):
        """Parse a configuration value into a series of lines,
        ignoring empty and comment lines"""
        if not lines:
            return []
        lines = [
            line.strip() for line in lines.splitlines()
            if line.strip() and not line.strip().startswith('#')]
        if relative_to:
            lines = [os.path.normpath(os.path.join(relative_to, line))
                     for line in lines]
        return lines

    def activate_services(self, environ=None):
        """Activates all the services for this application/configuration.

        Note, this doesn't create databases, this only typically sets
        environmental variables indicating runtime configuration."""
        if environ is None:
            environ = os.environ
        for service in self.service_list:
            environ.update(service.env_setup())
        if is_production():
            environ['SILVER_VERSION'] = 'silverlining/0.0'
        if is_production() and pwd.getpwuid(os.getuid())[0] == 'www-data':
            tmp = environ['TEMP'] = os.path.join('/var/lib/silverlining/tmp/', self.app_name)
            if not os.path.exists(tmp):
                os.makedirs(tmp)
        elif not environ.get('TEMP'):
            environ['TEMP'] = '/tmp'
        environ['SILVER_LOGS'] = self.log_dir
        if not is_production() and not os.path.exists(environ['SILVER_LOGS']):
            os.makedirs(environ['SILVER_LOGS'])
        if is_production():
            config_dir = os.path.join('/var/lib/silverlining/configs', self.app_name)
            if os.path.exists(config_dir):
                environ['SILVER_APP_CONFIG'] = config_dir
            elif self.config_default:
                environ['SILVER_APP_CONFIG'] = self.config_default
        else:
            if self.local_config:
                environ['SILVER_APP_CONFIG'] = self.local_config
            elif self.config_default:
                environ['SILVER_APP_CONFIG'] = self.config_default
            elif self.config_required:
                raise Exception('This application requires configuration and config.devel '
                                'is not set and no --config was given')
        return environ

    @property
    def log_dir(self):
        if is_production():
            return os.path.join('/var/log/silverlining/apps', self.app_name)
        else:
            return os.path.join(self.app_dir, 'silver-logs')

    def install_services(self, clear=False):
        """Installs all the services for this application.

        This is run on deployment"""
        for service in self.service_list:
            if clear:
                service.clear()
            else:
                service.install()

    def load_service_module(self, service_name):
        """Load the service module for the given service name"""
        __import__('silversupport.service.%s' % service_name)
        mod = sys.modules['silversupport.service.%s' % service_name]
        return mod

    def clear_services(self):
        for service in self.service_list:
            service.clear(self)

    def backup_services(self, dest_dir):
        for service in self.service_list:
            service_dir = os.path.join(dest_dir, service.name)
            if not os.path.exists(service_dir):
                os.makedirs(service_dir)
            service.backup(service_dir)

    def restore_services(self, source_dir):
        for service in self.service_list:
            service_dir = os.path.join(source_dir, service.name)
            service.restore(service_dir)

    def activate_path(self):
        """Adds any necessary entries to sys.path for this app"""
        lib_path = os.path.join(
            self.app_dir, 'lib', 'python%s' % sys.version[:3], 'site-packages')
        if lib_path not in sys.path and os.path.exists(lib_path):
            addsitedir(lib_path)
        sitecustomize = os.path.join(
            self.app_dir, 'lib', 'python%s' % sys.version[:3], 'sitecustomize.py')
        if os.path.exists(sitecustomize):
            ns = {'__file__': sitecustomize, '__name__': 'sitecustomize'}
            execfile(sitecustomize, ns)

    def get_app_from_runner(self):
        """Returns the WSGI app that the runner indicates
        """
        assert self.platform == 'python', (
            "get_app_from_runner() shouldn't be run on an app with the platform %s"
            % self.platform)
        runner = self.runner
        if '#' in runner:
            runner, spec = runner.split('#', 1)
        else:
            spec = None
        if runner.endswith('.ini'):
            try:
                from paste.deploy import loadapp
            except ImportError:
                print >> sys.stderr, (
                    "To use a .ini runner (%s) you must have PasteDeploy "
                    "installed in your application." % runner)
                raise
            from silversupport.secret import get_secret
            runner = 'config:%s' % runner
            global_conf = os.environ.copy()
            global_conf['SECRET'] = get_secret()
            app = loadapp(runner, name=spec,
                          global_conf=global_conf)
        elif runner.endswith('.py'):
            ## FIXME: not sure what name to give it
            ns = {'__file__': runner, '__name__': 'main_py'}
            execfile(runner, ns)
            spec = spec or 'application'
            if spec in ns:
                app = ns[spec]
            else:
                raise Exception("No application %s defined in %s"
                                % (spec, runner))
        else:
            raise Exception("Unknown kind of runner (%s)" % runner)
        if is_production() and is_disabled(self.app_name):
            disabled_appconfig = AppConfig.from_location('disabled')
            return DisabledSite(app, disabled_appconfig.get_app_from_runner())
        else:
            return app

    def canonical_hostname(self):
        """Returns the 'canonical' hostname for this application.

        This only applies in production environments."""
        from silversupport import appdata
        fp = open(appdata.APPDATA_MAP)
        hostnames = []
        instance_name = self.instance_name
        for line in fp:
            if not line.strip() or line.strip().startswith('#'):
                continue
            hostname, path, data = line.split(None, 2)
            line_instance_name = data.split('|')[0]
            if line_instance_name == instance_name:
                if hostname.startswith('.'):
                    hostname = hostname[1:]
                hostnames.append(hostname)
        hostnames.sort(key=lambda x: len(x))
        if hostnames:
            return hostnames[0]
        else:
            return None

    def write_php_env(self, filename=None):
        """Writes out a PHP file that loads up all the environmental variables

        This is because we don't run any Python during the actual
        request cycle for PHP applications.
        """
        assert self.platform == 'php'
        if filename is None:
            filename = os.path.join(self.app_dir, 'silver-env-variables.php')
        fp = open(filename, 'w')
        fp.write('<?\n')
        env = {}
        self.activate_services(env)
        for name, value in sorted(env.iteritems()):
            fp.write('$_SERVER[%s] = %r;\n' % (name, value))
        fp.write('?>')
        fp.close()

    def sync(self, host, instance_name):
        """Synchronize this application (locally) with a remote server
        at the given host.
        """
        dest_dir = os.path.join(DEPLOYMENT_LOCATION, instance_name)
        self._run_rsync(host, self.app_dir, dest_dir)

    def sync_config(self, host, config_dir):
        """Synchronise the given configuration (locally) with a remote server
        at the given host (for this app/app_name)"""
        dest_dir = os.path.join('/var/lib/silverlining/configs', self.app_name)
        self._run_rsync(host, config_dir, dest_dir)

    def _run_rsync(self, host, source, dest):
        assert not is_production()
        exclude_from = os.path.join(os.path.dirname(__file__), 'rsync-exclude.txt')
        if not source.endswith('/'):
            source += '/'
        ## FIXME: does it matter if dest ends with /?
        cmd = ['rsync',
               '--recursive',
               '--links',              # Copy over symlinks as symlinks
               '--copy-unsafe-links',  # Copy symlinks that are outside of dir as real files
               '--executability',      # Copy +x modes
               '--times',              # Copy timestamp
               '--rsh=ssh',            # Use ssh
               '--delete',             # Delete files thta aren't in the source dir
               '--compress',
               #'--skip-compress=.zip,.egg', # Skip some already-compressed files
               '--exclude-from=%s' % exclude_from,
               '--progress',           # I don't think this does anything given --quiet
               '--quiet',
               source,
               os.path.join('%s:%s' % (host, dest)),
               ]
        run(cmd)

    def check_service_setup(self, logger):
        import traceback
        for service in self.service_list:
            try:
                warning = service.check_setup()
            except Exception, e:
                logger.notify(
                    'Error with service %s:' % service.name)
                logger.indent += 2
                try:
                    logger.info(
                        traceback.format_exc())
                    logger.notify('%s: %s' %
                                  (e.__class__.__name__, str(e)))
                finally:
                    logger.indent -= 2
            else:
                if warning:
                    logger.notify('Warning with service %s:' % service.name)
                    logger.indent += 2
                    try:
                        logger.notify(warning)
                    finally:
                        logger.indent -= 2
