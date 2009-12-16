#!/bin/sh

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync from"
    exit 2
fi

rsync -r root@$SERVER:/var/www/support .
rsync -r root@$SERVER:/etc/apache2/sites-enabled .
