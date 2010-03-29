"""MongoDB support"""

from silversupport.shell import run, apt_install
from silversupport.abstractservice import AbstractService


class Service(AbstractService):

    def install(self):
        #WARNING, this will only work on ubuntu 9.10
        #since we don't have official ubuntu packages we use 10gen's PPA

        #needed for add-apt-repository, perhaps we should just implement a command to append:
        apt_install(['python-software-properties'])

        #FIXME, add-apt-repository will duplicate if run twice:
        run(['add-apt-repository', "deb http://downloads.mongodb.org/distros/ubuntu 9.10 10gen"])
        run(['apt-get', 'update'])
        apt_install(['mongodb'])

        #TODO Check to see if the database is present like couch does, seudo code below

    #    app_name = app_config.app_name
    #    stdout,stderr = run('curl -s -N http://localhost:28017/???'
    #    dbs = eval(stdout)

    #    if app_name in dbs:
    #        print 'Database %s already exists' % app_name
    #    else:
    #        print 'Database %s does not exist; created.' % app_name
    #        run('curl -N -s -X PUT http://localhost:28017/???' % app_name,env)

    def env_setup(self):
        environ = {}
        app_name = self.app_config.app_name
        environ['CONFIG_MONGODB_DB'] = app_name
        environ['CONFIG_MONGODB_HOST'] = '127.0.0.1:5984'
        if self.devel:
            for name, value in self.devel_config.items():
                if name.startswith('mongodb.'):
                    name = name[len('mongodb.'):]
                    environ['CONFIG_MONGODB_%s' % name.upper()] = value
        return environ
