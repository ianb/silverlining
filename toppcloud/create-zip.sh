#!/usr/bin/env bash

pushd "$(dirname $BASH_SOURCE)/../"
VERSION="$(python setup.py --version)"
mkdir -p build
BUILD="build/toppcloud-$VERSION"

if [ "$VIRTUALENV" = "" ] ; then
    VIRTUALENV="virtualenv"
fi

$VIRTUALENV -p python2.6 $BUILD

$BUILD/bin/pip install \
  http://bitbucket.org/ianb/cmdutils/get/tip.gz#egg=cmdutils \
  https://svn.apache.org/repos/asf/incubator/libcloud/trunk/#egg=libcloud \
  simplejson
$BUILD/bin/python setup.py install

cp toppcloud/toppcloud-zip-command.py $BUILD/toppcloud.py
chmod +x $BUILD/toppcloud.py
mv $BUILD/lib/python2.6/site-packages $BUILD/lib.tmp
rm -r $BUILD/lib
mv $BUILD/lib.tmp $BUILD/lib
rm -r $BUILD/bin $BUILD/include
rm -r $BUILD/lib/pip-*.egg/ $BUILD/lib/setuptools.pth $BUILD/lib/setuptools-*.egg $BUILD/lib/easy-install.pth
find $BUILD -name '*.pyc' -exec rm {} \;
pushd dist/
zip toppcloud-${VERSION}.zip toppcloud-${VERSION}
popd
