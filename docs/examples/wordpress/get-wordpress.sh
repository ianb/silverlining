#!/usr/bin/env bash

HERE="$(dirname $BASH_SOURCE)"
echo "Checking out http://core.svn.wordpress.org/tags/2.9.1 to $HERE/wordpress"
svn co http://core.svn.wordpress.org/tags/2.9.1 "$HERE/wordpress"
cp wp-config.php "$HERE/wordpress"
