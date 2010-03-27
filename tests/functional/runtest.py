"""Functional test for Silver Lining."""

import os
import time
import re
import urllib
from scripttest import TestFileEnvironment

here = os.path.dirname(os.path.abspath(__file__))


def get_environment():
    env = TestFileEnvironment(os.path.join(here, 'test-data'))
    return env

stage_seq = ['create-node', 'setup-node', 'clean', 'update', 'update-path',
             'query', 'activation']


def run_stage(name, match):
    return match in stage_seq[stage_seq.index(name):]


def run_test(name, stage=None, ci=False):
    try:
        if stage is None:
            if name:
                stage = 'clean'
            else:
                stage = 'setup-node'
        env = get_environment()
        if not name:
            name = 'functest%s.example.com' % int(time.time())
            print 'Creating node %s' % name
            print env.run('silver --yes create-node --image-id=14362 --wait %s' % name,
                          expect_stderr=True)
        if run_stage(stage, 'setup-node'):
            print 'Setting up node %s' % name
            print env.run('silver --yes setup-node %s' % name,
                          expect_stderr=True)

        if run_stage(stage, 'clean'):
            print env.run('silver --yes deactivate --node=%s "*"' % name)
            print env.run('silver --yes clean-node %s' % name)

        if run_stage(stage, 'update'):
            print 'Doing update'
            result = env.run('silver --yes update "%s" %s'
                             % (os.path.join(here, 'example-app'), name),
                             expect_stderr=True)
            print result
            assert 'env CONFIG_COUCHDB_DB=functest' in result.stdout, result.stdout
            assert 'env CONFIG_COUCHDB_HOST=127.0.0.1:5984' in result.stdout, result.stdout
            assert 'env CONFIG_FILES=/var/lib/silverlining/apps/functest' in result.stdout, result.stdout
            assert 'env CONFIG_PG_DBNAME=functest' in result.stdout, result.stdout
            assert 'env CONFIG_PG_HOST=' in result.stdout, result.stdout
            assert 'env CONFIG_PG_PASSWORD=' in result.stdout, result.stdout
            assert 'env CONFIG_PG_PORT=' in result.stdout, result.stdout
            assert 'env CONFIG_PG_SQLALCHEMY=postgres://postgres@/functest' in result.stdout, result.stdout
            assert 'env CONFIG_PG_USER=www-mgr' in result.stdout, result.stdout
            assert 'env CONFIG_WRITABLE_ROOT=/var/lib/silverlining/writable-roots/functest' in result.stdout, result.stdout
            assert 'env SILVER_VERSION=silverlining/' in result.stdout, result.stdout
            result = env.run('silver --yes update --debug-single-process "%s" %s'
                             % (os.path.join(here, 'example-app'), name),
                             expect_stderr=True)
            print result
            resp = urllib.urlopen('http://%s/update' % name).read()
            print 'Got HTTP response:\n%s' % resp
            assert ('SILVER_CANONICAL_HOST=%s' % name) in resp
            assert 'wsgi.multiprocess=True' in resp
            assert 'wsgi.multithread=True' in resp
            assert "path='' '/update'" in resp

        if run_stage(stage, 'update-path'):
            print 'Doing update to path'
            result = env.run('silver --yes update "%s" %s/test'
                             % (os.path.join(here, 'example-app'), name),
                             expect_stderr=True)
            print result
            url = 'http://%s/test/update' % name
            resp = urllib.urlopen(url).read()
            print 'The actual HTTP response: (%s)' % url
            print resp

        if run_stage(stage, 'query'):
            print 'Doing query'
            result = env.run('silver --yes query %s' % name)
            print result
            assert 'Site: default-disabled' in result.stdout
            assert 'default-disabled: disabled/' in result.stdout
            assert 'functest' in result.stdout
            assert re.search(r'functest.*?: %s/' % name, result.stdout)

        if run_stage(stage, 'activation'):
            print env.run('silver --yes deactivate %s/test' % name)
            print env.run('silver --yes query %s' % name)
            print env.run('silver --yes activate %s prev' % name)
            print env.run('silver --yes query %s' % name)

    finally:
        print 'Name used: %s' % name
        if ci:
            print 'Cleaning up server'
            env.run('silver --yes destroy-node %s' % name)

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--name')
    parser.add_option('--stage')
    parser.add_option('--ci', action='store_true')
    options, args = parser.parse_args()
    run_test(options.name, options.stage or None, options.ci)
