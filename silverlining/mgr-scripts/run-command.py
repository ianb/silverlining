#!/usr/bin/env python
import sys
sys.path.insert(0, '/usr/local/share/silverlining/lib')
import os
from silversupport import appdata
from silversupport.appconfig import AppConfig


def main():
    args = sys.argv[1:]
    hostname, path = appdata.normalize_location(args[0])
    tmp_dir = args[1]
    command = args[2]
    rest = args[3:]
    instance_name = appdata.instance_for_location(hostname, path)
    if not instance_name:
        print 'No instance found attached to %s%s' % (hostname, path)
        return 1
    app_config = AppConfig.from_instance_name(instance_name)

    if tmp_dir and tmp_dir != 'NONE':
        rest = [
            r.replace('$TMP', tmp_dir)
            for r in rest]
    path = find_command_path(app_config.app_dir, command)
    check_command_python(path)
    os.environ['SILVER_VERSION'] = 'silverlining/0.0'
    app_config.activate_services()
    app_config.activate_path()
    # Buffering can happen because this isn't obviously hooked up to a
    # terminal (even though it is indirectly):
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.argv = [path] + rest
    os.chdir(app_config.app_dir)
    ns = {'__file__': path, '__name__': '__main__'}
    if os.path.basename(path) == 'ipython':
        ## ipython-specific hack
        if not os.access(os.environ['HOME'], os.W_OK):
            os.environ['HOME'] = '/tmp'
    os.chdir(app_config.app_dir)
    if os.path.basename(path) in ('python', 'python2.6'):
        from code import InteractiveConsole
        console = InteractiveConsole()
        console.interact()
    else:
        execfile(path, ns)


def find_command_path(app_dir, command_name):
    if command_name.startswith(os.path.sep):
        # Absolute path
        return command_name
    places = [os.path.join(app_dir, 'bin'),
              app_dir,
              '/bin',
              '/usr/bin']
    for place in places:
        place = os.path.join(place, command_name)
        if os.path.exists(place):
            return place
    print >> sys.stderr, (
        "%s not found (looked in %s)"
        % (command_name, ', '.join(places)))
    sys.exit(1000)


def check_command_python(path):
    if path.endswith('.py'):
        # Good enough
        return
    if path.endswith('python') or path.endswith('python2.6'):
        return
    fp = open(path)
    first = fp.readline()
    fp.close()
    if not first.startswith('#!'):
        print >> sys.stderr, (
            "Not a #! script: %s" % path)
        sys.exit(1001)
    if not 'python' in first:
        print >> sys.stderr, (
            "#! line in script is not for Python (%s): %s"
            % (first.strip(), path))
        sys.exit(1001)


if __name__ == '__main__':
    sys.exit(main())
