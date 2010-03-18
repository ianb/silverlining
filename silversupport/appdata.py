"""Routines for handling /var/www/appdata.map"""
from silversupport.appconfig import AppConfig

APPDATA_MAP = '/var/www/appdata.map'

def set_appdata(instance_name, locations, debug_single_process=False,
                add_prev=True):
    app_config = AppConfig.from_appinstance(instance_name)
    if debug_single_process:
        process_group = 'general_debug'
    else:
        process_group = 'general'
    locations = normalize_locations(locations)
    new_lines = rewrite_lines(appdata_lines(), locations, add_prev=True, dict(
        instance_name=instance_name, platform=app_config.platform,
        process_group=process_group, php_root=app_config.php_root,
        write_root=app_config.writable_root_location))
    fp = open(APPDATA_MAP, 'w')
    fp.writelines(new_lines)
    fp.close()

def rewrite_lines(existing, locations, add_prev, vars):
    if isinstance(existing, basestring):
        existing = existing.splitlines(True)
    lines = []
    for line in existing:
        if not line.strip() or line.strip().startswith('#'):
            lines.append(line)
            continue
        ex_hostname, ex_path, ex_data = line.split(None, 2)
        for hostname, path in locations:
            if add_prev:
                if 'prev.' + hostname == ex_hostname and path == ex_path:
                    # Overwrite the old (non-prev) hostname
                    break
                elif hostname == ex_hostname and path == ex_path:
                    # Rewrite matching lines to prev.
                    lines.append('prev.' + line)
            else:
                if hostname == ex_hostname and path == ex_path:
                    # Overwrite!
                    break
        else:
            lines.append(line)
    data = '%(instance_name)s|%(process_group)s|%(write_root)s|%(platform)s|%(php_root)s' % vars
    for hostname, path in locations:
        lines.append('%s %s %s\n' % (hostname, path, data))
    return ''.join(lines)

def normalize_locations(locations, empty_path='/'):
    new = []
    for location in locations:
        if location.startswith('http://'):
            location = location[len('http://'):]
        if location.startswith('https://'):
            location = location[len('https://'):]
        if '/' in location:
            hostname, path = location.split('/', 1)
            path = '/' + path
        else:
            hostname = location
            path = empty_path
        new.append((hostname, path))
    return new

def remove_host(hostname, keep_prev=False, path=None):
    """Updates /var/www/appdata.map to remove the given hostname.

    If `keep_prev` is True, then the prev.* hostname will be left
    in place, otherwise it will be deleted at the same time.

    If path is given the deletions will be limited to that path
    (or if it is a list, to those paths).

    This returns the list of lines removed.
    """
    new_lines = []
    if path and isinstance(path, basestring):
        path = [path]
    removed = []
    for line in appdata_lines():
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        line_hostname, line_path, data = line.split(None, 2)
        if (hostname == line_hostname
            or (not keep_prev and 'prev.'+hostname == line_hostname)):
            if not path or line_path in path:
                removed.append(line)
                continue
        new_lines.append(line)
    fp = open(APPDATA_MAP, 'w')
    fp.writelines(new_lines)
    fp.close()
    return removed

def appdata_lines():
    """Returns all lines in /var/www/appdata.map"""
    fp = open(APPDATA_MAP)
    try:
        return fp.readlines()
    finally:
        fp.close()

def instance_for_location(hostname, path='/'):
    """Returns the instance name for the given hostname/path.

    Returns None if no instance found"""
    for line in appdata_lines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        line_hostname, line_path, data = line.split(None, 2)
        if (line_hostname == hostname and line_path == path):
            instance_name = data.split('|')[0]
            return instance_name
    return None

