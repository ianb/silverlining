#!/bin/sh

SETUP="false"
if [ "$1" = "--setup" ] ; then
    shift
    SETUP="true"
fi

if [ $SETUP = true ] ; then
    echo "Installing rsync"
    ssh root@$SERVER "apt-get install rsync"
fi

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync to"
    exit 2
fi

echo rsync -rvC support/ root@$SERVER:/var/www/support/
rsync -rvC support/ root@$SERVER:/var/www/support/
echo rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/
rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/
echo rsync -rvC root/ root@$SERVER:/root/
rsync -rvC root/ root@$SERVER:/root/

if [ $SETUP = true ] ; then
    echo "Running apt-get install on server"
    awk '{print $1}' < dpkg-query.txt | ssh root@$SERVER 'apt-get install $(cat)'
fi

echo rsync -vC www-README.txt root@$SERVER:/var/www/README.txt
rsync -vC www-README.txt root@$SERVER:/var/www/README.txt
echo rsync -vC topp-setup root@$SERVER:/etc/init.d/topp-setup
rsync -vC topp-setup root@$SERVER:/etc/init.d/topp-setup
echo rsync -vC pg_hba.conf root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf
rsync -vC pg_hba.conf root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf



ssh root@$SERVER "
mkdir -p /var/topp/build-files
mkdir -p /var/log/topp-setup
mkdir -p /var/www
chown www-mgr:www-mgr /var/www
chown -R root:root /var/www/support
if [ ! -e /var/www/hostmap.txt ] ; then
    touch /var/www/hostmap.txt
    chown www-mgr:www-mgr /var/www/hostmap.txt
fi
chmod +x /etc/init.d/topp-setup
rcconf --on=topp-setup
if ! psql -l | grep template_postgis ; then
    createdb template_postgis
    for N in lwpostgis.sql lwpostgis_upgrade.sql spatial_ref_sys.sql ; do
        psql template_postgis < /usr/share/postgresql-8.3-postgis/$N
    done
fi
if [ ! -e /home/www-mgr ] ; then
    adduser --disabled-password www-mgr
fi
"
