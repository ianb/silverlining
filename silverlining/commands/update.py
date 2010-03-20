"""Update/deploy an application"""
import re
import os
from cmdutils import CommandError
import virtualenv
from silverlining.etchosts import get_host_ip, set_etc_hosts
from silversupport.shell import ssh
from silversupport.appconfig import AppConfig
from silversupport import appdata

_instance_name_re = re.compile(r'instance_name="(.*?)"')


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
    app = AppConfig(os.path.join(config.args.dir, 'app.ini'),
                    app_name=config.args.name or None)
    if not config.args.location:
        if app.default_location:
            config.args.location = app.default_location
        else:
            config.args.location = config.node_hostname
    if not config.args.node:
        from silversupport.appdata import normalize_location
        config.args.node = normalize_location(config.args.location)[0]
    stdout, stderr, returncode = ssh(
        'www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/prepare-new-site.py %s' % app.app_name,
        capture_stdout=True, capture_stderr=True)
    match = _instance_name_re.search(stdout)
    if not match:
        config.logger.fatal("Did not get the new instance_name from prepare-new-site.py")
        config.logger.fatal("Output: %s (stderr: %s)" % (stdout, stderr))
        raise Exception("Bad instance_name output")
    instance_name = match.group(1)
    assert instance_name.startswith(app.app_name), instance_name
    app.sync('www-mgr@%s' % config.node_hostname, instance_name)
    ssh('root', config.node_hostname,
        'python -m compileall -q /var/www/%(instance_name)s; '
        '/usr/local/share/silverlining/mgr-scripts/update-service.py %(instance_name)s'
        % dict(instance_name=instance_name))

    if config.args.debug_single_process:
        debug_single_process = '--debug-single-process'
    else:
        debug_single_process = ''

    ssh('www-mgr', config.node_hostname,
        '/usr/local/share/silverlining/mgr-scripts/update-appdata.py %(instance_name)s %(debug_single_process)s %(location)s; '
        'sudo -H -u www-data /usr/local/share/silverlining/mgr-scripts/internal-request.py --update %(instance_name)s %(location)s; '
        'sudo -H -u www-data pkill -INT -f -u www-data wsgi; '
        % dict(instance_name=instance_name,
               debug_single_process=debug_single_process,
               location=config.args.location),
        )

    ip = get_host_ip(config.node_hostname)
    hostname = appdata.normalize_location(config.args.location)[0]
    set_etc_hosts(config, [hostname,
                           'prev.' + hostname], ip)
