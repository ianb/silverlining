"""Creates ~/.silverlining.conf

This builds the file from a template, and asks the user some questions
about how to build it.
"""

import os
import tempita

template = tempita.Template.from_filename(
    os.path.join(os.path.dirname(__file__), 'silverlining.conf.tmpl'))

silverlining_conf = os.path.join(os.environ['HOME'], '.silverlining.conf')


def create_conf():
    """Create a brand-new ~/.silverlining.conf"""
    print 'Creating %s' % silverlining_conf
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
        silverlining_location=os.path.dirname(__file__),
        )
    fp = open(silverlining_conf, 'w')
    fp.write(content)
    fp.close()
