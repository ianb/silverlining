export PGUSER=postgres
if [ ! -e /home/www-mgr ] ; then
    adduser --disabled-password --gecos=none www-mgr
    mkdir -p /home/www-mgr/.ssh
    cp /root/.ssh/authorized_keys /home/www-mgr/.ssh/authorized_keys
    chown -R www-mgr:www-mgr /home/www-mgr/.ssh/
fi
chown postgres:postgres /etc/postgresql/8.3/main/pg_hba.conf
NEED_RESTART=F
if [ ! -e /etc/apache2/mods-enabled/rewrite.load ] ; then
    pushd /etc/apache2/mods-enabled
    ln -s ../mods-available/rewrite.load
    popd
    NEED_RESTART=T
fi
if [ ! -e /var/www/hostmap.txt ] ; then
    touch /var/www/hostmap.txt
    chown www-mgr:www-mgr /var/www/hostmap.txt
fi
if [ -e /etc/apache2/sites-enabled/000-default ] ; then
    rm /etc/apache2/sites-enabled/000-default
    NEED_RESTART=T
fi
if [ "$NEED_RESTART" = T ] ; then
    /etc/init.d/apache2 restart
fi
/etc/init.d/postgresql-8.3 restart
/etc/init.d/varnish restart
mkdir -p /var/topp/build-files
mkdir -p /var/log/topp-setup
mkdir -p /var/www
rm -f /var/www/index.html
chown www-mgr:www-mgr /var/www
chown -R root:root /var/www/support
sed -i "s/ -backup/-backup/" /etc/joe/jmacsrc
chmod +x /etc/init.d/topp-setup
rcconf --on=topp-setup
if ! psql -l | grep template_postgis ; then
    createdb template_postgis
    echo 'CREATE LANGUAGE plpgsql' | psql template_postgis
    for N in lwpostgis.sql lwpostgis_upgrade.sql spatial_ref_sys.sql ; do
        psql template_postgis < /usr/share/postgresql-8.3-postgis/$N
    done
fi
touch /root/.toppcloud-server-setup
