"""Get a secret key"""

def get_secret():
    fp = open('/var/lib/toppcloud/secret.txt', 'rb')
    return fp.read().strip()
