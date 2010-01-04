## This might not be necessary, because we shouldn't really be doing
## anything related to postgres; but what this does is make all
## postgres-related commands use the user postgres:
export PGUSER=postgres

## Set up a standard user for managing apps (www-mgr)
if [ ! -e /home/www-mgr ] ; then
    ## --gecos=none suppresses the querying for name, room #, etc.:
    adduser --disabled-password --gecos=none www-mgr
    mkdir -p /home/www-mgr/.ssh
    cp /root/.ssh/authorized_keys /home/www-mgr/.ssh/authorized_keys
    chown -R www-mgr:www-mgr /home/www-mgr/.ssh/
fi

## rsync won't handle permissions; but probably this shouldn't be
## necessary as service.postgis handles this:
if [ -e /etc/init.d/postgresql-8.3 ] ; then
    chown postgres:postgres /etc/postgresql/8.3/main/pg_hba.conf
fi

## This creates the default /var/hostmap.txt, which points to the two
## standard notfound/disabled apps:
if [ ! -e /var/www/hostmap.txt ] ; then
    echo "notfound default-notfound
disabled default-disabled" > /var/www/hostmap.txt
    chown www-mgr:www-mgr /var/www/hostmap.txt
fi

## Now setup Apache.  Ubuntu installs 000-default, which we don't
## want, so we delete it, and make sure the necessary modules are
## enabled:
a2enmod rewrite
a2enmod headers
a2enmod deflate
if [ -e /etc/apache2/sites-enabled/000-default ] ; then
    rm /etc/apache2/sites-enabled/000-default
fi

## These are restarted in the background, to make it faster:
/etc/init.d/apache2 restart &
/etc/init.d/varnish restart &

## This is probably unnecessary...
if [ -e /etc/init.d/postgresql-8.3 ] ; then
    /etc/init.d/postgresql-8.3 restart &
fi

## Make sure some standard directories are in place, ownership is
## correct, etc.:
mkdir -p /var/topp/build-files
mkdir -p /var/log/topp-setup
mkdir -p /var/www
rm -f /var/www/index.html
chown www-mgr:www-mgr /var/www
chown -R root:root /var/www/support
chmod +x /etc/init.d/topp-setup
rcconf --on=topp-setup

# (this should give a date or something)
touch /root/.toppcloud-server-setup
## This is just a piece of configuration I (Ian) like:
sed -i "s/ -backup/-backup/" /etc/joe/jmacsrc
