from silversupport.shell import apt_install


class AbstractService(object):
    name = None

    # Any deb packages that need to be installed:
    packages = []
    # This should be like {'python': ['python-mydb']}
    # Packages that depend on the python/php platform
    platform_packages = {}

    def __init__(self, app_config, config_string, devel=False,
                 devel_config=None, output=None):
        self.app_config = app_config
        self.config_string = config_string
        self.devel = devel
        self.devel_config = devel_config
        if output:
            self.output = output
        else:
            self.output = self.stdout_output
        self.env = self.env_setup()

    def __repr__(self):
        return '<%s.%s for %r>' % (
            self.__class__.__module__, self.__class__.__name__,
            self.app_config)

    def stdout_output(self, msg):
        print msg

    def install(self):
        """Installs everything for this service.  This may have to
        install packages, configure the service, and probably has to
        setup a database for the application."""
        raise NotImplementedError

    def install_packages(self):
        """Install any (deb) packages needed for this service.

        This will read the class variables packages and
        platform_packages by default.

        Implementations of ``.install()`` should probably call this
        method."""
        packages = (self.packages +
                    self.platform_packages.get(self.app_config.platform, []))
        apt_install(packages)

    def env_setup(self):
        """Returns an environment dictionary of any variables that
        should be set"""
        raise NotImplementedError

    def backup(self, output_dir):
        """Backs up this database into a directory"""
        raise NotImplementedError

    def restore(self, input_dir):
        """Restores this database from the given backup (unpacked)"""
        raise NotImplementedError

    def clear(self):
        """Clears the database"""
        raise NotImplementedError

    def check_setup(self):
        """This runs a check on the service, especially for use in
        development.

        For instance, you could connect to a database to make sure it
        is setup and available.

        This should raise an exception if there's a serious problem,
        or return a string warning if it's a suspected or non-fatal
        problem.
        """
        pass
