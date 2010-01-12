import re
import os
import subprocess
from cmdutils import CommandError
import virtualenv
## FIXME: circular import:
from toppcloud.runner import App
from toppcloud.etchosts import get_host_ip, set_etc_hosts

_instance_name_re = re.compile(r'app_dir="(.*?)"')

def command_update(config):
    if not os.path.exists(config.args.dir):
        raise CommandError(
            "No directory in %s" % config.args.dir)
    if not config.args.name:
        config.args.name = os.path.basename(os.path.abspath(config.args.dir))
        config.logger.info('Using app name=%r' % config.args.name)
    config.logger.info('Fixing up .pth and .egg-info files')
    virtualenv.logger = config.logger
    virtualenv.fixup_pth_and_egg_link(
        config.args.dir,
        [os.path.join(config.args.dir, 'lib', 'python2.6'),
         os.path.join(config.args.dir, 'lib', 'python2.6', 'site-packages'),
         os.path.join(config.args.dir, 'lib', 'python')])
    app = App(config.args.dir, config.args.name, config.args.host)
    if not config.args.host:
        if app.config['production'].get('default_host'):
            config.args.host = app.config['production']['default_host']
        else:
            config.args.host = config.node_hostname
    ssh_host = '%s@%s' % (config['remote_username'], config.node_hostname)
    ssh_root_host = 'root@%s' % config.node_hostname
    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/prepare-new-site.py %s %s' % (app.site_name, app.version)],
        stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    match = _instance_name_re.search(stdout)
    if not match:
        config.logger.fatal("Did not get the new instance_name from prepare-new-site.py")
        config.logger.fatal("Output: %s" % stdout)
        raise Exception("Bad instance_name output")
    instance_name = match.group(1)
    assert instance_name.startswith(app.site_name)
    app.sync(ssh_host, instance_name)
    proc = subprocess.Popen(
        ['ssh', ssh_root_host,
         'python -m compileall -q /var/www/%(instance_name)s; '
         '/var/www/support/update-service.py %(instance_name)s'
         % dict(instance_name=instance_name),
         ])
    proc.communicate()

    proc = subprocess.Popen(
        ['ssh', ssh_host,
         '/var/www/support/update-hostmap.py %(instance_name)s %(host)s %(version)s.%(host)s; '
         'sudo -u www-data /var/www/support/internal-request.py update %(instance_name)s %(host)s; '
         'sudo -u www-data pkill -INT -f -u www-data wsgi; '
         % dict(instance_name=instance_name,
                host=config.args.host,
                version=app.version),
         ])
    proc.communicate()

    ip = get_host_ip(config.node_hostname)
    set_etc_hosts(config, [config.args.host,
                           '%s.%s' % (app.version, config.args.host),
                           'prev.' + config.args.host], ip)