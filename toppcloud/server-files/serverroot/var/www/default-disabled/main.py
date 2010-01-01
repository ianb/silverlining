import os

fp = open(os.path.join(os.path.dirname(__file__), 'static', 'disabled.html'), 'rb')
disabled = fp.read()
fp.close()

def application(environ, start_response):
    start_response('503 Service Unavailable', 
                   [('Content-type', 'text/html; charset=UTF-8'),
                    ('Content-Length', str(len(disabled))),
                    ('Cache-Control', 'no-store, no-cache, max-age=0'),
                    ('Pragma', 'no-cache')])
    return [disabled]
