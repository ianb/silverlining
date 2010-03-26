import os
from silverlining import tmplconfig

here = os.path.dirname(os.path.abspath(__file__))


def test_config():
    conf = tmplconfig.Configuration(
        os.path.join(here, 'test_tmplconfig.ini'))
    assert conf.general.name == 'my-server-setup'
    assert tmplconfig.asbool(conf.general.set_etc_hosts) is False
    assert getattr(conf.general, 'foobar', None) is None
    os.environ['FAKE_HOME'] = '/my-home'
    assert conf.provider['secret_file'] == '{{environ.FAKE_HOME}}/.rackspace-secret.txt'
    assert conf.provider.secret_file == '/my-home/.rackspace-secret.txt'
    assert tmplconfig.lines(conf.appserver.locations) == ['http://foobar.com/ APP_NAME1']
    sec = conf.sections('service:')['mysql']
    assert int(sec.nodes) == 1
    s = unicode(conf.balancer)
    s = s.replace(here, 'HERE')
    assert s == u"""\
# Without special support, generally just 1 node is supported
# also node_name/size
[balancer]
# From HERE/test_tmplconfig.ini:
# Describes the load balancer
node_name = balancer.foobar.com
hostnames = foobar.com
    baz.com""", s
