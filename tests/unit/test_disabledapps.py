"""Tests for the functionality around disabled applications"""
import os
import os.path
import tempfile
from contextlib import contextmanager, nested
import sys
import shutil

from webtest import TestApp

from silversupport import disabledapps
from silversupport.appconfig import AppConfig
from silversupport import appdata

ROOT = os.path.join(os.path.dirname(__file__),  '../..')


@contextmanager
def monkeypatch(module, global_, replacement):
    """Replace module.global_ with replacement"""
    if isinstance(module, str):
        __import__(module)
        module = sys.modules[module]
    old = getattr(module, global_)
    setattr(module, global_, replacement)
    try:
        yield
    finally:
        setattr(module, global_, old)


@contextmanager
def temporary_directory():
    """Make and then remove a temporary directory"""
    dirname = tempfile.mkdtemp()
    try:
        yield dirname
    finally:
        shutil.rmtree(dirname)


@contextmanager
def patch_disabled_apps_path(dirname):
    """Changes the location of the disabled apps list to be within dirname

    Returns the new path of the file
    """
    with monkeypatch(disabledapps, 'DISABLED_APPS_FILE',
                     os.path.join(dirname, 'disabledapps.txt')):
        try:
            yield disabledapps.DISABLED_APPS_FILE
        finally:
            if os.path.exists(disabledapps.DISABLED_APPS_FILE):
                os.remove(disabledapps.DISABLED_APPS_FILE)


def test_addition():
    """Adding an application should correctly write the file"""
    with temporary_directory() as tempdir:
        with patch_disabled_apps_path(tempdir) as path:
            disabledapps.disable_application('testapp')
            with open(path) as file_:
                lines = [line.strip() for line in file_]
                assert lines == ['testapp'], lines


def test_is_disabled():
    """We should be able to identify disabled apps"""
    with temporary_directory() as tempdir:
        with patch_disabled_apps_path(tempdir):
            assert not disabledapps.is_disabled('testapp')
            disabledapps.disable_application('testapp')
            assert disabledapps.is_disabled('testapp')


def test_removal():
    """Removing applications should work correctly"""
    with temporary_directory() as tempdir:
        with patch_disabled_apps_path(tempdir) as path:
            disabledapps.disable_application('testapp-a')
            disabledapps.disable_application('testapp-b')
            disabledapps.disable_application('testapp-c')
            disabledapps.enable_application('testapp-b')
            with open(path) as file_:
                lines = [line.strip() for line in file_]
                assert lines == ['testapp-a', 'testapp-c'], lines


## Utilities to help set up a disabled site
def patch_deployment_location(dirname):
    """Replace /var/www with dirname, and set is_production to True"""
    return nested(
        patch_disabled_apps_path(dirname),
        monkeypatch(appdata, 'APPDATA_MAP',
                    os.path.join(dirname, 'appdata.map')),
        monkeypatch('silversupport.appconfig', 'DEPLOYMENT_LOCATION', dirname),
        monkeypatch('silversupport.appconfig', 'is_production', lambda: True))


def install_default_disabled(dirname):
    """Copy default-disabled into dirname"""
    default_disabled = os.path.join(
        ROOT, 'silverlining/server-root/var/www/default-disabled')
    shutil.copytree(default_disabled,
                    os.path.join(dirname, 'default-disabled'))
    with open(os.path.join(dirname, 'appdata.map'), 'w') as file_:
        file_.write(
            "disabled / default-disabled|general_debug|/dev/null|python|\n")


def install_sample_app(dirname):
    """copy sample app into dirname"""
    path = os.path.join(dirname, 'sampleapp.0')
    os.mkdir(path)
    with open(os.path.join(path, 'app.ini'), 'w') as file_:
        file_.write('[production]\n')
        file_.write('app_name = sampleapp\n')
        file_.write('runner = app.py#application\n')
    with open(os.path.join(path, 'app.py'), 'w') as file_:
        file_.write(
            'from wsgiref.simple_server import demo_app as application\n')
    appdata.add_appdata('sampleapp.0', ['www.example.com'])


@contextmanager
def disabled_site():
    with temporary_directory() as tempdir:
        with patch_deployment_location(tempdir):

            install_default_disabled(tempdir)
            install_sample_app(tempdir)
            disabledapps.disable_application('sampleapp')

            app_config = AppConfig.from_location('www.example.com')
            app = app_config.get_app_from_runner()
            yield app


def test_loading_disabled_site():
    """Loading a site should return a DisabledSite when the site is disabled"""
    with disabled_site() as app:
        assert isinstance(app, disabledapps.DisabledSite), app


def test_disabled_site_is_disabled():
    with disabled_site() as app:
        test_app = TestApp(app)
        response = test_app.get(
            '/', headers={'X-Forwarded-For':'123.123.123.123, localhost'},
            status=503)


def test_disabled_site_commandline_internal_access():
    with disabled_site() as app:
        test_app = TestApp(app)
        response = test_app.get(
            '/', headers={'X-Forwarded-For':'123.123.123.123, localhost'},
            extra_environ={'silverlining.update': True},
            status=200)
        assert response.body.startswith('Hello world!'), str(response)


def test_disabled_site_local_access():
    with disabled_site() as app:
        test_app = TestApp(app)
        response = test_app.get(
            '/', headers={'X-Forwarded-For':'localhost, localhost'})
        assert response.status.startswith('200')
        assert response.body.startswith('Hello world!')
