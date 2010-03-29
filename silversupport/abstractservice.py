from silversupport.shell import apt_install


class AbstractService(object):
    name = None

    packages = []
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
        raise NotImplementedError

    def install_packages(self):
        packages = (self.packages +
                    self.platform_packages.get(self.app_config.platform, []))
        apt_install(packages)

    def env_setup(self):
        raise NotImplementedError

    def backup(self, output_dir):
        raise NotImplementedError

    def restore(self, input_dir):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
