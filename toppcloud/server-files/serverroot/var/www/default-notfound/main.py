import os

fp = open(os.path.join(os.path.dirname(__file__), 'static', 'not_found.html'), 'rb')
not_found = fp.read()
fp.close()

def application(environ, start_response):
    start_response('404 Not Found', 
                   [('Content-type', 'text/html; charset=UTF-8'),
                    ('Content-Length', str(len(not_found)))])
    return [not_found]
