"""Clear all the data from an application instance"""
from silversupport.shell import ssh
from silversupport.appdata import normalize_location


def command_clear(config):
    ## FIXME: this has to be root for bad reasons (it'll try to reinstall the services)
    stdout, stderr, returncode = ssh(
        'root', normalize_location(config.args.location)[0],
        '/usr/local/share/silverlining/mgr-scripts/update-service.py --location=%(location)s --clear; '
        'sudo -H -u www-data /usr/local/share/silverlining/mgr-scripts/internal-request.py --update-location %(location)s; '

        % dict(location=config.args.location))
