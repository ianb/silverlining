#!/bin/sh

# This fixes some weird problems...
LANG=C
export LANG

if [ "$1" = "--auth" ] ; then
    shift
    echo "Setting up auth for $1"
    cat ~/.ssh/id_dsa.pub | ssh root@$1 "
mkdir -p /root/.ssh
cat >> /root/.ssh/authorized_keys
"
    exit
fi

SETUP="false"
if [ "$1" = "--setup" ] ; then
    shift
    SETUP="true"
fi

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync to"
    exit 2
fi

if [ $SETUP = true ] ; then
    echo "Installing rsync"
    ssh root@$SERVER "apt-get update ; apt-get install rsync"
fi

echo rsync -rvC root/ root@$SERVER:/root/
rsync -rvC root/ root@$SERVER:/root/

if [ $SETUP = true ] ; then
    echo "Running apt-get install on server"
    awk '{print $1}' < dpkg-query.txt | ssh root@$SERVER 'apt-get install $(cat)'
fi

echo rsync -rvC support/ root@$SERVER:/var/www/support/
rsync -rvC support/ root@$SERVER:/var/www/support/
echo rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/
rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/

echo rsync -vC www-README.txt root@$SERVER:/var/www/README.txt
rsync -vC www-README.txt root@$SERVER:/var/www/README.txt
echo rsync -vC topp-setup root@$SERVER:/etc/init.d/topp-setup
rsync -vC topp-setup root@$SERVER:/etc/init.d/topp-setup
echo rsync -vC pg_hba.conf root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf
rsync -vC pg_hba.conf root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf

ssh root@$SERVER '
export PGUSER=postgres
if [ ! -e /home/www-mgr ] ; then
    adduser --disabled-password --gecos=none www-mgr
    mkdir -p /home/www-mgr/.ssh
    cp /root/.ssh/authorized_keys /home/www-mgr/.ssh/authorized_keys
    chown -R www-mgr:www-mgr /home/www-mgr/.ssh/
fi
if [ -e /etc/init.d/postgresql-8.3 ] ; then
    chown postgres:postgres /etc/postgresql/8.3/main/pg_hba.conf
fi
pushd /etc/apache2/mods-enabled
ln -s ../mods-available/rewrite.load
popd
if [ ! -e /var/www/hostmap.txt ] ; then
    touch /var/www/hostmap.txt
    chown www-mgr:www-mgr /var/www/hostmap.txt
fi
rm /etc/apache2/sites-enabled/000-default
/etc/init.d/apache2 restart
if [ -e /etc/init.d/postgresql-8.3 ] ; then
    /etc/init.d/postgresql-8.3 restart
fi
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
'
