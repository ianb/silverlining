Hello, and welcome to your new Silver Lining layout.

Note that new packages will be installed in lib/python (*not*
lib/python2.6).  Only the "basic" packages (pip, setuptools) will be
in lib/python2.6.  The idea is that you can put lib/python directly in
version control, as a static record of exactly what you have
installed.

Other packages that you don't install from a release should go in
src/, and installed via setup.py develop.  There will be a record in
lib/python/easy-install.pth of these files.

There are some absolute paths that get put into the environment, but
Silver Lining makes these paths relative before uploading (since it
will be uploaded into a different location).

