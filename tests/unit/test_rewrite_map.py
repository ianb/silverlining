import os
import new
from cStringIO import StringIO

rewrite_map_fn = os.path.abspath(os.path.join(
    __file__, '../../../silverlining/mgr-scripts/rewrite-map.py'))

rewritemap = new.module('rewritemap')
rewritemap.__file__ = rewrite_map_fn
execfile(rewrite_map_fn, rewritemap.__dict__)

def test_rewrite_map():
    data = StringIO("""\
test1.example.com / test1-root
test1.example.com /testy test1-testy
test1.example.com /testy/another test1-another
test2.example.com seeother test1.example.com
.example.com / example-generic
* /blog all-blog
* / all-root
""")
    rewritemap.read_file_data(data)
    assert 'test1.example.com' in rewritemap.abs_hostnames, (
        rewritemap.abs_hostnames)
    
    assert '*' in rewritemap.glob_hostnames, (
        rewritemap.glob_hostnames)
    assert '.example.com' in rewritemap.glob_hostnames
    tests = """\
test1.example.com^/ / test1-root
test1.example.com^/something / test1-root
test1.example.com^/testy/something /testy test1-testy
test1.example.com^/testy/another/something /testy/another test1-another
test2.example.com^/testy/ /testy test1-testy
foobar.example.com^/ / example-generic
nothing.notfound^/foo / all-root
nothing.notfound^/blog/foo /blog all-blog""".splitlines()
    for line in tests:
        input, output = line.split(None, 1)
        hostname, path = input.split('^')
        path_match, data = rewritemap.lookup(hostname, path)
        result = '%s %s' % (path_match, data)
        assert result == output, (
            "Bad result: %r -> %r" % (line, result))

def test_appdata():
    from silversupport import appdata
    locations = ['http://foo.com/bar', 'example.com/',
                 'test1.example.com', 'example.com/blog']
    assert appdata.normalize_locations(locations) == (
        [('foo.com', '/bar'), ('example.com', '/'),
         ('test1.example.com', '/'), ('example.com', '/blog')])
    existing = """\
# Here are some lines:
example.com / app_name.1|general|/dev/null|python|
example.com /blog blog_name|general|/var/lib/silverlining/app/writable-roots/blog_name|python|
example.com /wiki media_name|general|/dev/null|php|mediawiki
"""
    vars = dict(app_name='app_name.2', platform='python',
                php_root='', process_group='general_debug',
                write_root='/dev/null')
    new = appdata.rewrite_lines(existing, [('example.com', '/'), ('test2.example.com', '/stage')],
                                vars)
    assert new == """\
# Here are some lines:
example.com /blog blog_name|general|/var/lib/silverlining/app/writable-roots/blog_name|python|
example.com /wiki media_name|general|/dev/null|php|mediawiki
example.com / app_name.2|general_debug|/dev/null|python|
test2.example.com /stage app_name.2|general_debug|/dev/null|python|
"""

if __name__ == '__main__':
    test_rewrite_map()
    test_appdata()
