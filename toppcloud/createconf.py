import os
import tempita

template = tempita.Template.from_filename(
    os.path.join(os.path.dirname(__file__), 'toppcloud.conf.tmpl'))

toppcloud_conf = os.path.join(os.environ['HOME'], '.toppcloud.conf')

def create_conf():
    print 'Creating %s' % toppcloud_conf
    username = raw_input('Your service-provider username: ')
    api_key = raw_input('Your service-provider API key: ')
    for path in ['id_rsa.pub', 'id_dsa.pub']:
        pubkey_path = os.path.join(os.environ['HOME'], '.ssh', path)
        if os.path.exists(pubkey_path):
            print 'Using %s' % pubkey_path
            fp = open(pubkey_path)
            pubkey = fp.read().strip()
            fp.close()
            break
    else:
        pubkey = None
        print "%s doesn't exist" % pubkey_path
        print "  you won't automatically be able to login to new servers"
    content = template.substitute(
        username=username, api_key=api_key, pubkey=pubkey,
        toppcloud_location=os.path.dirname(__file__),
        )
    fp = open(toppcloud_conf, 'w')
    fp.write(content)
    fp.close()
    
