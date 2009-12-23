#!/bin/sh

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync from"
    exit 2
fi

rsync -r root@$SERVER:/var/www/support .
rsync -r root@$SERVER:/etc/apache2/sites-enabled .
rsync -r root@$SERVER:/root .

for F in .bash_history .debtags .joe_state .lesshst .psql_history .ssh ; do
    if [ -e root/$F ] ; then
        rm -rf root/$F
    fi
done
