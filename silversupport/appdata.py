"""Routines for handling /var/www/appdata.map"""
from silversupport.appconfig import AppConfig

APPDATA_MAP = '/var/www/appdata.map'

def set_appdata(instance_name, locations, debug_single_process=False):
    app_config = AppConfig.from_appinstance(instance_name)
    if debug_single_process:
        process_group = 'general_debug'
    else:
        process_group = 'general'
    locations = normalize_locations(locations)
    fp = open(APPDATA_MAP)
    existing = fp.read()
    fp.close()
    new_lines = rewrite_lines(existing, locations, dict(
        instance_name=instance_name, platform=app_config.platform,
        process_group=process_group, php_root=app_config.php_root,
        write_root=app_config.writable_root_location))
    fp = open(APPDATA_MAP, 'w')
    fp.writelines(new_lines)
    fp.close()

def rewrite_lines(existing, locations, vars):
    if isinstance(existing, basestring):
        existing = existing.splitlines(True)
    lines = []
    for line in existing:
        if not line.strip() or line.strip().startswith('#'):
            lines.append(line)
            continue
        ex_hostname, ex_path, ex_data = line.split(None, 2)
        for hostname, path in locations:
            if hostname == ex_hostname and path == ex_path:
                # Overwrite!
                break
        else:
            lines.append(line)
    data = '%(instance_name)s|%(process_group)s|%(write_root)s|%(platform)s|%(php_root)s' % vars
    for hostname, path in locations:
        lines.append('%s %s %s\n' % (hostname, path, data))
    return ''.join(lines)

def normalize_locations(locations):
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
            path = '/'
        new.append((hostname, path))
    return new
