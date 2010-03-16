import re
import os
from cmdutils import CommandError
import virtualenv
## FIXME: circular import:
from silverlining.runner import App
from silverlining.etchosts import get_host_ip, set_etc_hosts
from silversupport.shell import ssh

_instance_name_re = re.compile(r'app_dir="(.*?)"')

def command_update(config):
    if not os.path.exists(config.args.dir):
        raise CommandError(
            "No directory in %s" % config.args.dir)
    config.logger.info('Fixing up .pth and .egg-info files')
    virtualenv.logger = config.logger
    config.logger.indent += 2
    config.logger.level_adjust += -1
    try:
        virtualenv.fixup_pth_and_egg_link(
            config.args.dir,
            [os.path.join(config.args.dir, 'lib', 'python2.6'),
             os.path.join(config.args.dir, 'lib', 'python2.6', 'site-packages'),
             os.path.join(config.args.dir, 'lib', 'python')])
    finally:
        config.logger.indent -= 2
        config.logger.level_adjust -= -1
    app = App(config.args.dir, config.args.name, config.args.host)
    if not config.args.host:
        if app.config['production'].get('default_host'):
            config.args.host = app.config['production']['default_host']
        else:
            config.args.host = config.node_hostname
    stdout, stderr, returncode = ssh(
        'www-mgr', config.node_hostname,
        '/var/www/support/prepare-new-site.py %s %s' % (app.site_name, app.version),
        capture_stdout=True)
    match = _instance_name_re.search(stdout)
    if not match:
        config.logger.fatal("Did not get the new instance_name from prepare-new-site.py")
        config.logger.fatal("Output: %s" % stdout)
        raise Exception("Bad instance_name output")
    instance_name = match.group(1)
    assert instance_name.startswith(app.site_name)
    app.sync('www-mgr@%s' % config.node_hostname, instance_name)
    ssh('root', config.node_hostname,
        'python -m compileall -q /var/www/%(instance_name)s; '
        '/var/www/support/update-service.py %(instance_name)s'
        % dict(instance_name=instance_name))

    if config.args.debug_single_process:
        debug_single_process = '--debug-single-process'
    else:
        debug_single_process = ''

    ssh('www-mgr', config.node_hostname,
        '/var/www/support/update-hostmap.py %(instance_name)s %(debug_single_process)s %(host)s %(version)s.%(host)s; '
        'sudo -H -u www-data /var/www/support/internal-request.py --update %(instance_name)s %(host)s; '
        'sudo -H -u www-data pkill -INT -f -u www-data wsgi; '
        % dict(instance_name=instance_name,
               debug_single_process=debug_single_process,
               host=config.args.host,
               version=app.version),
        )

    ip = get_host_ip(config.node_hostname)
    set_etc_hosts(config, [config.args.host,
                           '%s.%s' % (app.version, config.args.host),
                           'prev.' + config.args.host], ip)
