import os
import tempita

template = tempita.Template.from_filename(
    os.path.join(os.path.dirname(__file__), 'toppcloud.conf.tmpl'))

toppcloud_conf = os.path.join(os.environ['HOME'], '.toppcloud.conf')

def create_conf():
    print 'Creating %s' % toppcloud_conf
    username = raw_input('Your service-provider username: ')
    api_key = raw_input('Your service-provider API key: ')
    dsa_filename = os.path.join(os.environ['HOME'], '.ssh', 'id_dsa.pub')
    if os.path.exists(dsa_filename):
        print 'Using %s' % dsa_filename
        fp = open(dsa_filename)
        id_dsa = fp.read().strip()
        fp.close()
    else:
        print "%s doesn't exist" % dsa_filename
        print "  you won't automatically be able to login to new servers"
        id_dsa = None
    content = template.substitute(
        username=username, api_key=api_key, id_dsa=id_dsa,
        toppcloud_location=os.path.dirname(__file__),
        )
    fp = open(toppcloud_conf, 'w')
    fp.write(content)
    fp.close()
    
