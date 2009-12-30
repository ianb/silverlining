import os

SITE_DIR = '/var/www'

def sites():
    sites = []
    for name in os.listdir(SITE_DIR):
        if (name != 'support' 
            and os.path.isdir(os.path.join(SITE_DIR, name)):
            sites.append(name)
    return sites
