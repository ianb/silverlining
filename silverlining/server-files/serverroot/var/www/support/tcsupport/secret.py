"""Get a secret key"""
import os
from ConfigParser import ConfigParser

if os.environ.get('SILVER_VERSION', '').startswith('silverlining/'):
    secret_file = '/var/lib/silverlining/secret.txt'
    key_file = '/var/lib/silverlining/keys.ini'
else:
    secret_file = os.path.join(
        os.environ['HOME'], '.silverlining-secret')
    if not os.path.exists(secret_file):
        import base64
        fp = open(secret_file, 'wb')
        secret = base64.b64encode(os.urandom(24), "_-").strip("=")
        fp.write(secret)
        fp.close()
    key_file = os.path.join(
        os.environ['HOME'], '.silverlining.conf')

def get_secret():
    fp = open(secret_file, 'rb')
    return fp.read().strip()

def get_key(name):
    keys = load_keys()
    return keys.get(name)

def load_keys():
    parser = ConfigParser()
    parser.read([key_file])
    keys = {}
    if parser.has_section('keys'):
        for option in parser.options('keys'):
            keys[option] = parser.get('keys', option)
    for section in parser.sections():
        if section.startswith('keys:'):
            name = section[len('keys:'):]
            keys[name] = {}
            for option in parser.options(section):
                keys[name][option] = parser.get(section, option)
    return keys
