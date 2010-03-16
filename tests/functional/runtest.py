"""Functional test for Silver Lining."""

import os
import time
from scripttest import TestFileEnvironment
import subprocess

here = os.path.dirname(os.path.abspath(__file__))

def get_environment():
    env = TestFileEnvironment(os.path.join(here, 'test-data'))
    return env

def run_test(name):
    try:
        env = get_environment()
        if not name:
            name = 'functest%s.example.com' % int(time.time())
            print 'Creating and setting up node %s' % name
            print env.run('silver --yes create-node --image-id=14362 --setup-node %s' % name,
                          expect_stderr=True)
            #proc = subprocess.Popen('silver --yes create-node --image-id=14362 --setup-node %s' % name)
            #proc.communicate()
        print 'Doing update'
        result = env.run('silver --yes update --node=%s --host=%s "%s"'
                         % (name, name, os.path.join(here, 'example-app')),
                         expect_stderr=True)
        print result
        assert 'env CONFIG_COUCHDB_DB=functest' in result.stdout
        assert 'env CONFIG_COUCHDB_HOST=127.0.0.1:5984' in result.stdout
        assert 'env CONFIG_FILES=/var/lib/silverlining/apps/functest' in result.stdout
        assert 'env CONFIG_PG_DBNAME=functest' in result.stdout
        assert 'env CONFIG_PG_HOST=' in result.stdout
        assert 'env CONFIG_PG_PASSWORD=' in result.stdout
        assert 'env CONFIG_PG_PORT=' in result.stdout
        assert 'env CONFIG_PG_SQLALCHEMY=postgres://postgres@/functest' in result.stdout
        assert 'env CONFIG_PG_USER=www-mgr' in result.stdout
        assert 'env CONFIG_WRITABLE_ROOT=/var/lib/silverlining/writable-roots/functest' in result.stdout
        assert 'env SILVER_VERSION=silverlining/' in result.stdout
        result = env.run('silver --yes update --node=%s --host=%s --debug-single-process "%s"'
                         % (name, name, os.path.join(here, 'example-app')),
                         expect_stderr=True)
        print result
    finally:
        print 'Name used: %s' % name

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('--name')
    options, args = parser.parse_args()
    run_test(options.name)
    
