#!/usr/bin/env bash

pushd "$(dirname $BASH_SOURCE)/../"
VERSION="$(python setup.py --version)"
mkdir -p zip-build
BUILD="zip-build/toppcloud-$VERSION"

if [ "$VIRTUALENV" = "" ] ; then
    VIRTUALENV="virtualenv"
fi

if [ -e "$BUILD" ] ; then
    rm -rf $BUILD
fi

$VIRTUALENV -p python2.6 $BUILD

$BUILD/bin/pip install \
  http://bitbucket.org/ianb/cmdutils/get/tip.gz#egg=cmdutils \
  https://svn.apache.org/repos/asf/incubator/libcloud/trunk/#egg=libcloud \
  simplejson \
  -e .
$BUILD/bin/python setup.py install --single-version-externally-managed --record zip-build/record.txt

cp toppcloud/toppcloud-zip-command.py $BUILD/toppcloud.py
chmod +x $BUILD/toppcloud.py
mv $BUILD/lib/python2.6/site-packages $BUILD/lib.tmp
rm -r $BUILD/lib
mv $BUILD/lib.tmp $BUILD/lib
rm -r $BUILD/bin $BUILD/include $BUILD/build
rm -r $BUILD/lib/pip-*.egg/ $BUILD/lib/setuptools.pth $BUILD/lib/setuptools-*.egg $BUILD/lib/easy-install.pth
find $BUILD -name '*.pyc' -exec rm {} \;
pushd zip-build
zip -r toppcloud-${VERSION}.zip toppcloud-${VERSION}
mv toppcloud-${VERSION}.zip ../dist
popd