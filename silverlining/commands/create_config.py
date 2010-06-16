"""Clear all the data from an application instance"""
import os
import re
import shutil
from cmdutils import CommandError
import tempita
from silversupport.appconfig import AppConfig
from silversupport.util import read_config

def command_create_config(config):
    app = AppConfig(os.path.join(config.args.dir, 'app.ini'))
    settings = os.path.join(app.config_template, 'template.ini')
    if not os.path.exists(settings):
        settings = {}
    else:
        settings = read_config(settings)
    if not app.config_template:
        config.logger.fatal('The application has no config.template')
        return 1
    if config.args.info:
        return show_info(config, app, settings)
    variables = {}
    for expr in config.args.variable:
        if '=' not in expr:
            raise CommandError(
                'The argument %s should be in the form var=value' % expr)
        var_name, value = expr.split('=', 1)
        variables[var_name] = value
    for var_name, desc in sorted(settings.get('variables', {}).items()):
        if var_name in variables:
            continue
        value = raw_input('%s (%s): ' % (var_name, desc))
        variables[var_name] = value
    fill_directory(app.config_template,
                   config.args.output,
                   variables,
                   skip_files='./template.ini')

def show_info(config, app, settings):
    l = config.logger
    if not settings:
        l.notify('The application has no template.ini in %s' % app.config_template)
        return
    l.notify('The variables that can be substituted in the files:')
    for v, desc in sorted(settings.get('variables', {}).items()):
        l.notify('  %s:' % v)
        ## FIXME: wrap better:
        l.notify('    %s' % desc)

def fill_directory(source, dest, variables, skip_files=()):
    variables.setdefault('dot', '.')
    source = os.path.abspath(source)
    for dirpath, dirnames, filenames in os.walk(source):
        for dirname in list(dirnames):
            if dirname in skip_files:
                dirnames.remove(dirname)
        for filename in list(filenames):
            if filename in skip_files:
                filenames.remove(filename)
        for filename in filenames:
            if filename.startswith('.'):
                continue
            source_filename = os.path.join(dirpath, filename)
            assert source_filename.startswith(source)
            path = source_filename[len(source):].lstrip('/')
            path = render_filename(path, variables)
            is_template = filename.endswith('.tmpl')
            dest_filename = os.path.join(dest, path)
            if is_template:
                dest_filename = dest_filename[:-5]
            dest_dir = os.path.dirname(dest_filename)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            if is_template:
                source_content = render_source(source_filename, variables)
            else:
                source_content = file_content(source_filename)
            if os.path.exists(dest_filename):
                if file_content(dest_filename) == source_content:
                    continue
                backup_file(dest_filename)
            fp = open(dest_filename, 'wb')
            fp.write(source_content)

_var_re = re.compile(r'\+(.*?)\+')

def render_filename(path, variables):
    return _var_re.sub(lambda m: variables[m.group(1)], path)

def render_source(filename, variables):
    if os.path.splitext(filename)[1].lower() in ('.html', '.htm'):
        TemplateClass = tempita.HTMLTemplate
    else:
        TemplateClass = tempita.Template
    template = TemplateClass.from_filename(filename)
    return template.substitute(variables)

def file_content(filename):
    fp = open(filename, 'rb')
    c = fp.read()
    fp.close()
    return c

def backup_file(filename):
    n = 1
    while 1:
        new_fn = '%s.%s' % (filename, n)
        if not os.path.exists(new_fn):
            break
        n += 1
    shutil.copyfile(filename, new_fn)
