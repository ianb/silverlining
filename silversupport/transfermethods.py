import os
from silversupport.shell import run
import warnings
warnings.filterwarnings('ignore', r'tempnam is a potential security risk')


def local(dir, dest):
    if is_archive(dest):
        archive(dir, dest)
    else:
        run(['cp', '-ar', dir, dest])


def ssh(dir, dest):
    if is_archive(dest):
        tmp = make_temp_name(dest)
        try:
            archive(dir, tmp)
            run(['scp', '-p', tmp, dest])
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    else:
        run(['scp', '-rp', dir, dest])


def rsync(dir, dest):
    if is_archive(dest):
        tmp = make_temp_name(dest)
        try:
            archive(dir, tmp)
            run(['rsync', '-t', dir, dest])
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    else:
        run(['rsync', '-rt', dir, dest])


def make_temp_name(dest):
    name = os.tempnam() + extension(dest)
    return name


def is_archive(name):
    return extension(name) in ('.zip', '.tar.gz', '.tar.bz2', '.tgz', 'tbz2')


def extension(name):
    path, ext = os.path.splitext(name)
    if ext in ('.gz', '.bz2'):
        ext = os.path.splitext(path)[1] + ext
    return ext


def archive(dir, dest):
    ext = extension(dest)
    if ext == '.zip':
        run(['zip', '-r', '--symlinks', dest, dir])
    elif ext in ('.tar.gz', '.tgz', '.tar.bz2', '.tbz2'):
        if ext in ('.tar.gz', '.tgz'):
            op = 'z'
        else:
            op = 'j'
        run(['tar', op + 'fc', dest, '.'],
            cwd=dir)
    else:
        assert 0, 'unknown extension %r' % ext
