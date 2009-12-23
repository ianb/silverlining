#!/bin/sh

SERVER="$1"
if [ "$SERVER" = "" ] ; then
    echo "You must give a server to sync from"
    exit 2
fi

echo rsync -r root@$SERVER:/var/www/support .
rsync -r root@$SERVER:/var/www/support .
echo rsync -r root@$SERVER:/etc/apache2/sites-enabled .
rsync -r root@$SERVER:/etc/apache2/sites-enabled .
echo rsync -r root@$SERVER:/root .
rsync -r root@$SERVER:/root .
echo rsync root@$SERVER:/var/www/README.txt www-README.txt
rsync root@$SERVER:/var/www/README.txt www-README.txt
echo rsync root@$SERVER:/etc/init.d/topp-setup topp-setup
rsync root@$SERVER:/etc/init.d/topp-setup topp-setup
echo rsync root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf pg_hba.conf
rsync root@$SERVER:/etc/postgresql/8.3/main/pg_hba.conf pg_hba.conf
echo ssh root@$SERVER '"dpkg-query -W" >' dpkg-query.txt
ssh root@$SERVER "dpkg-query -W" > dpkg-query.txt

for F in .bash_history .debtags .joe_state .lesshst .psql_history .ssh ; do
    if [ -e root/$F ] ; then
        rm -rf root/$F
    fi
done
