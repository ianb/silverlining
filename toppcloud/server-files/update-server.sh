#!/bin/sh

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync to"
    exit 2
fi

echo rsync -rvC support/ root@$SERVER:/var/www/support/
rsync -rvC support/ root@$SERVER:/var/www/support/
echo rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/
rsync -rvC sites-enabled/ root@$SERVER:/etc/apache2/sites-enabled/
