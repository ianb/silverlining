"""Set up a new silver/virtualenv environment"""
import os
import sys
import virtualenv
from silversupport.shell import run


def command_init(config):
    dir = config.args.dir
    app_name = os.path.basename(os.path.abspath(dir))
    vars = dict(
        app_name=app_name,
        main=config.args.main,
        config=config.args.config)
    vars['force'] = config.args.force
    if sys.version[:3] == '2.6':
        virtualenv.logger = config.logger
        virtualenv.create_environment(
            dir,
            # This should be true to pick up global binaries like psycopg:
            site_packages=True,
            unzip_setuptools=True,
            use_distribute=config.args.distribute)
    else:
        # This is the crude way we need to do this when we're not in Python 2.6
        config.logger.warn('Creating virtualenv environment in subprocess')
        virtualenv_file = virtualenv.__file__
        if virtualenv_file.endswith('.pyc'):
            virtualenv_file = virtualenv_file[:-1]
        if config.args.distribute:
            cmd = [
                '/usr/bin/python2.6', virtualenv_file,
                '--unzip-setuptools', '--distribute',
                dir]
        else:
            cmd = [
                '/usr/bin/python2.6', virtualenv_file,
                '--unzip-setuptools', dir]
        run(cmd)
    noforce_vars = vars.copy()
    noforce_vars['force'] = False
    init_copy('README.txt', os.path.join(dir, 'README.txt'), config.logger, noforce_vars)
    init_copy('app.ini', os.path.join(dir, 'app.ini'), config.logger, noforce_vars)
    if config.args.config:
        init_copy('config.ini', os.path.join(dir, 'config.ini'), config.logger, vars)
    if config.args.main:
        init_copy('main.py', os.path.join(dir, 'main.py'), config.logger, vars)
    src = os.path.join(dir, 'src')
    if not os.path.exists(src):
        os.mkdir(src)
    static = os.path.join(dir, 'static')
    if not os.path.exists(static):
        os.mkdir(static)
    lib_python = os.path.join(dir, 'lib', 'python')
    if not os.path.exists(lib_python):
        os.makedirs(lib_python)
    #XXX this is a hack around http://bitbucket.org/ianb/silverlining/issue/1/bug-on-running-silver-init-for-the-second
    distutils_dir = os.path.join(dir, 'lib', 'python2.6', 'distutils')
    if os.path.islink(distutils_dir):
        distutils_init = os.path.join(dir, 'lib', 'python2.6', 'distutils', '__init__.py')
        _distutils_init_content = open(distutils_init).read()
        os.unlink(distutils_dir)
        os.makedirs(distutils_dir)
        init_copystring(
            _distutils_init_content,
            distutils_init,
            config.logger, vars, append=True)

    init_copy(
        'sitecustomize.py',
        os.path.join(dir, 'lib', 'python2.6', 'sitecustomize.py'),
        config.logger, vars)
    init_copystring(
        _distutils_cfg,
        os.path.join(dir, 'lib', 'python2.6', 'distutils', 'distutils.cfg'),
        config.logger, vars, append=True)
    init_copystring(
        _distutils_init,
        os.path.join(dir, 'lib', 'python2.6', 'distutils', '__init__.py'),
        config.logger, vars, append=True)
    init_copystring(
        _activate_this,
        os.path.join(dir, 'bin', 'activate_this.py'),
        config.logger, vars, append=True)
_distutils_cfg = """\
# This is what makes things install into lib/python instead of lib/python2.6:
[install]
home = <sys.prefix>
"""

_distutils_init = """\

# Patch by silverlining:
old_parse_config_files = dist.Distribution.parse_config_files
def parse_config_files(self, filenames=None):
    old_parse_config_files(self, filenames)
    opt_dict = self.get_option_dict('install')
    if 'home' in opt_dict:
        location, value = opt_dict['home']
        if value.lower().strip() == 'default':
            del opt_dict['home']
        else:
            opt_dict['home'] = (location, value.replace('<sys.prefix>', sys.prefix))
dist.Distribution.parse_config_files = parse_config_files
"""

_activate_this = """\

# Added by silverlining:
# This is some extra code to make activate_this.py run sitecustomize:
sitecustomize = os.path.abspath(os.path.join(__file__, '../../lib/python%s/sitecustomize.py' % sys.version[:3]))
if os.path.exists(sitecustomize):
    execfile(sitecustomize, dict(__file__=sitecustomize, __name__='sitecustomize'))
"""


def init_copy(source, dest, logger, vars, append=False):
    import tempita
    source = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'init-files',
        source)
    if os.path.exists(source+'.tmpl'):
        source = source+'.tmpl'
        template = tempita.Template.from_filename(source)
        source_content = template.substitute(vars)
    else:
        fp = open(source, 'rb')
        source_content = fp.read()
        fp.close()
    init_copystring(source_content, dest, logger, vars,
                    append=append)


def init_copystring(source_content, dest, logger, vars,
                    append=False):
    if os.path.exists(dest):
        fp = open(dest, 'rb')
        content = fp.read()
        fp.close()
        if append:
            if content in source_content:
                logger.info(
                    'Not adding to %s (already has content)' % dest)
                return
        else:
            if content == source_content:
                logger.info(
                    'Not overwriting %s (same content)' % dest)
                return
            elif vars['force']:
                logger.notify(
                    'Overwriting %s' % dest)
            else:
                logger.notify(
                    'Not overwriting %s (content differs)' % dest)
                return
    if append:
        fp = open(dest, 'ab')
    else:
        fp = open(dest, 'wb')
    fp.write(source_content)
    fp.close()
