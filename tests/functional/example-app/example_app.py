import os
import sys
import traceback


def application(environ, start_response):
    try:
        path_info = environ['PATH_INFO']
        if path_info == '/update':
            body = []
            for name, value in sorted(os.environ.items()):
                if name.startswith('SILVER') or name.startswith('CONFIG_'):
                    body.append('env %s=%s' % (name, value))
            body.append('wsgi.multiprocess=%r' % environ['wsgi.multiprocess'])
            body.append('wsgi.multithread=%r' % environ['wsgi.multithread'])
            body.append('path=%r %r' % (environ['SCRIPT_NAME'], environ['PATH_INFO']))
            body.append('Update run.')
            body = '\n'.join(body)
        elif path_info == '/write-root':
            write_root = os.environ['CONFIG_WRITABLE_ROOT']
            host = environ['HTTP_HOST'].split(':')[0]
            host_dir = os.path.join(write_root, host)
            if not os.path.exists(host_dir):
                os.mkdir(host_dir)
            open(os.path.join(write_root, 'test-writable.txt'), 'w').write('test writable')
            open(os.path.join(host_dir, 'test-hosted.txt'), 'w').write('test hosted')
            body = 'WRITABLE_ROOT=%s' % write_root
        else:
            body = 'INSTANCE=%s' % os.environ['SILVER_INSTANCE_NAME']
        start_response('200 OK', [('Content-type', 'text/plain')])
        environ['wsgi.errors'].write('Executed application\n')
        print 'This is stdout'
        print >> sys.stderr, 'This is stderr'
        return [body]
    except:
        start_response('500 Server Error', [('Content-type', 'text/plain')])
        exc = traceback.format_exc()
        return [exc]
