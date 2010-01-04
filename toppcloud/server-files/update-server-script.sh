export PGUSER=postgres
if [ ! -e /home/www-mgr ] ; then
    adduser --disabled-password --gecos=none www-mgr
    mkdir -p /home/www-mgr/.ssh
    cp /root/.ssh/authorized_keys /home/www-mgr/.ssh/authorized_keys
    chown -R www-mgr:www-mgr /home/www-mgr/.ssh/
fi
if [ ! -e /etc/apache2/mods-enabled/rewrite.load ] ; then
    pushd /etc/apache2/mods-enabled
    ln -s ../mods-available/rewrite.load
    popd
fi
if [ ! -e /var/www/hostmap.txt ] ; then
    echo "notfound default-notfound
disabled default-disabled" > /var/www/hostmap.txt
    chown www-mgr:www-mgr /var/www/hostmap.txt
fi
a2enmod headers
a2enmod deflate
if [ -e /etc/apache2/sites-enabled/000-default ] ; then
    rm /etc/apache2/sites-enabled/000-default
fi
# These are restarted in the background, to make it faster:
/etc/init.d/apache2 restart &
/etc/init.d/varnish restart &
# This must be synchronous, because it has to come up before we can continue:
mkdir -p /var/topp/build-files
mkdir -p /var/log/topp-setup
mkdir -p /var/www
rm -f /var/www/index.html
chown www-mgr:www-mgr /var/www
chown -R root:root /var/www/support
sed -i "s/ -backup/-backup/" /etc/joe/jmacsrc
chmod +x /etc/init.d/topp-setup
rcconf --on=topp-setup
touch /root/.toppcloud-server-setup
