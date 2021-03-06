## Fix locale
locale-gen en_US en_US.UTF-8
dpkg-reconfigure locales
update-locale LANG=en_US.UTF-8

## Set up a standard user for managing apps (www-mgr)
if [ ! -e /home/www-mgr ] ; then
    ## --gecos=none suppresses the querying for name, room #, etc.:
    adduser --disabled-password --gecos=none www-mgr
    mkdir -p -m 700 /home/www-mgr/.ssh
    cp /root/.ssh/authorized_keys /home/www-mgr/.ssh/authorized_keys
    chown -R www-mgr:www-mgr /home/www-mgr/.ssh/
    chmod 600 /home/www-mgr/.ssh/*
fi

## Make www-data part of the adm group, which means it can read
## /var/log/apache2 and other log files
adduser www-data adm > /dev/null # output is boring

# For some reason this is only readable by root:
chmod a+r /etc/hosts


if [ ! -e /var/www/appdata.map ] ; then
    echo "not-found / default-notfound|general_debug|/dev/null/|python|
disabled / default-disabled|general_debug|/dev/null|python|
" > /var/www/appdata.map
fi
touch /var/www/disabledapps.txt
chown www-mgr:www-mgr /var/www/appdata.map /var/www/disabledapps.txt

## Now setup Apache.  Ubuntu installs 000-default, which we don't
## want, so we delete it, and make sure the necessary modules are
## enabled:
a2enmod rewrite > /dev/null
a2enmod headers > /dev/null
a2enmod deflate > /dev/null
if [ -e /etc/apache2/sites-enabled/000-default ] ; then
    rm /etc/apache2/sites-enabled/000-default
fi

## These are restarted in the background, to make it faster:
echo "Restarting apache2 and varnish"
/etc/init.d/apache2 restart &>/dev/null &
/etc/init.d/varnish restart &>/dev/null &

## Make sure some standard directories are in place, ownership is
## correct, etc.:
mkdir -p /var/silverlining/build-files
mkdir -p /var/log/silverlining-setup
mkdir -p /var/log/silverlining
mkdir -p /var/log/silverlining/apps
chown www-data:www-data /var/log/silverlining/apps
mkdir -p /var/www
mkdir -p /var/lib/silverlining
mkdir -p /var/lib/silverlining/backups
mkdir -p /var/lib/silverlining/tmp
mkdir -p /var/lib/silverlining/configs
chown www-data:www-data /var/lib/silverlining/tmp
rm -f /var/www/index.html
chown www-mgr:www-mgr /var/www /var/lib/silverlining/backups /var/lib/silverlining/configs
chown -R root:root /usr/local/share/silverlining/
# Sometimes it has been reported that the executable bit isn't rsync'd over properly:
chmod 755 /usr/local/share/silverlining/mgr-scripts/*.py
chmod 0440 /etc/sudoers
chown www-mgr:www-mgr /var/lib/silverlining
# Make sure the support files are compiled:
python -m compileall -q /usr/local/share/silverlining/lib/
python -m compileall -q /usr/local/share/silverlining/mgr-scripts/

## This is just a piece of configuration I (Ian) like:
sed -i "s/ -backup/-backup/" /etc/joe/jmacsrc

## Make sure there's a secret:
if [ ! -e /var/lib/silverlining/secret.txt ] ; then
    python -c '
import os, base64, sys
secret = base64.b64encode(os.urandom(24), "_-").strip("=")
sys.stdout.write(secret)' > /var/lib/silverlining/secret.txt
    chown root /var/lib/silverlining/secret.txt
fi

echo "Rerun setup-node on $(date)
Run by: __REMOTE_USER__
----------------------------------------

" >> /var/log/silverlining/setup-node.log
