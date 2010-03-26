"""Template-based configuration file"""

import os
from UserDict import DictMixin
from initools.configparser import ConfigParser, NoOptionError
from tempita import Template

__all__ = ['Configuration', 'asbool', 'lines']


class TmplParser(ConfigParser):
    """Parser customized for use with this configuration"""
    global_section = True
    case_sensitive = True
    section_case_sensitive = True
    inherit_defaults = False
    extendable = True
    ignore_missing_files = False


class EnvironWrapper(DictMixin):
    """Handily wraps os.environ allowing attribute access"""

    def __init__(self, environ):
        self.environ = environ

    def __getitem__(self, item):
        return self.environ[item]

    def __setitem__(self, item, value):
        self.environ[item] = value

    def __delitem__(self, item):
        del self.environ[item]

    def keys(self):
        return self.environ.keys()

    def __contains__(self, item):
        return item in self.environ

    def __getattr__(self, attr):
        return self.get(attr)

    def __repr__(self):
        if self.environ is os.environ:
            return '<EnvironWrapper for os.environ>'
        else:
            return '<EnvironWrapper for %r>' % self.environ

    def __str__(self):
        lines = []
        for name, value in sorted(self.environ.items()):
            lines.append('%s=%r' % (name, value))
        return '\n'.join(lines)


class NoDefault:
    pass


class Configuration(DictMixin):
    """Handy configuration object that does template expansion"""

    def __init__(self, filenames=None):
        self._parser = TmplParser()
        if filenames:
            self.parse_files(filenames)
        self._ns = dict(
            config=self,
            environ=EnvironWrapper(os.environ))
        self._sections = {}

    def set_variable(self, name, value=NoDefault):
        if value is NoDefault:
            if name in self._ns:
                del self._ns[name]
        else:
            self._ns[name] = value

    def parse_files(self, filenames):
        if isinstance(filenames, basestring):
            filenames = [filenames]
        self._parser.read(filenames)

    def __getitem__(self, item):
        if item in self._sections:
            return self._sections[item]
        if self._parser.has_section(item):
            section = self._sections[item] = _Section(self, item)
            return section
        else:
            raise KeyError('No section [%s]' % item)

    def keys(self):
        return self._parser.sections()

    def sections(self, prefix=None):
        result = {}
        if prefix is None:
            for name, sec in self.items():
                result[name] = sec
        else:
            for name, sec in self.items():
                if name.startswith(prefix):
                    name = name[len(prefix):]
                    result[name] = sec
        return result

    def __contains__(self, item):
        return self._parser.has_section(item)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('No section %s' % item)

    def __str__(self):
        return unicode(self).encode('utf8')

    def __unicode__(self, section_name=None):
        lines = []
        p = self._parser
        cur_filename = None
        for sec in p._section_order:
            if section_name and sec != section_name:
                continue
            ## FIXME: there's a problem with [DEFAULT] here:
            sec_obj = self[sec]
            comment = p._section_comments.get(sec)
            if comment:
                lines.append(_add_hash(comment))
            lines.append('[%s]' % p._pre_normalized_sections[sec])
            ops = p._section_key_order[sec]
            for op in ops:
                filename = p.setting_location(sec, op)[0]
                if filename != cur_filename:
                    lines.append('# From %s:' % filename)
                    cur_filename = filename
                comment = p._key_comments.get((sec, op))
                if comment:
                    lines.append(_add_hash(comment))
                value = sec_obj[op]
                value_lines= value.splitlines()
                lines.append('%s = %s' % (p._pre_normalized_keys[(sec, op)], value_lines[0]))
                lines.extend('    %s' % v for v in value_lines[1:])
                try:
                    rendered = getattr(sec_obj, op)
                except Exception, e:
                    lines.append('# %s rendering error: %s' % (op, e))
                if rendered != value:
                    rendered_lines = rendered.splitlines()
                    lines.append('# %s rendered: %s' % (op, rendered_lines[0]))
                    lines.extend('#              %s' % l for l in rendered_lines[1:])
        return '\n'.join(lines)


class _Section(DictMixin):
    """Object to represent one section"""

    def __init__(self, config, section_name):
        self._config = config
        self._section_name = section_name
        self._ns = self._config._ns.copy()
        self._ns['section'] = self

    def set_variable(self, name, value=NoDefault):
        if value is NoDefault:
            if name in self._ns:
                del self._ns[name]
        else:
            self._ns[name] = value

    def __getitem__(self, item):
        try:
            return self._config._parser.get(self._section_name, item)
        except NoOptionError:
            raise KeyError('No option [%s] %s' % (self._section_name, item))

    def keys(self):
        return self._config._parser.options(self._section_name)

    def __contains__(self, item):
        return self._config._parser.has_option(self._section_name, item)

    def __getattr__(self, item):
        try:
            value = self[item]
        except KeyError, e:
            raise AttributeError(str(e))
        filename, line_number = self._config._parser.setting_location(
            self._section_name, item)
        name = '[%s] %s (in %s:%s)' % (self._section_name, item, filename, line_number)
        tmpl = Template(value, name=name)
        return tmpl.substitute(self._ns)

    def __repr__(self):
        return 'Configuration()[%r]' % (self._section_name)

    def __unicode__(self):
        return self._config.__unicode__(self._section_name)

    def __str__(self):
        return self._config.__unicode__(self._section_name).encode('utf8')


def asbool(obj):
    if isinstance(obj, (str, unicode)):
        obj = obj.strip().lower()
        if obj in ['true', 'yes', 'on', 'y', 't', '1']:
            return True
        elif obj in ['false', 'no', 'off', 'n', 'f', '0']:
            return False
        else:
            raise ValueError(
                "String is not true/false: %r" % obj)
    return bool(obj)


def lines(obj):
    if not obj:
        return []
    if isinstance(obj, basestring):
        obj = obj.splitlines()
        return [
            l.strip() for l in obj
            if l.strip() and not l.strip().startswith('#')]
    return obj


def _add_hash(comment):
    return '\n'.join('#'+l for l in comment.splitlines())
