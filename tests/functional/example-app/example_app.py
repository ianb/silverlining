import os
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
            body.append('Update run.')
            body = '\n'.join(body)
        else:
            body = 'hi'
        start_response('200 OK', [('Content-type', 'text/plain')])
        return [body]
    except:
        start_response('500 Server Error', [('Content-type', 'text/plain')])
        exc = traceback.format_exc()
        return [exc]

