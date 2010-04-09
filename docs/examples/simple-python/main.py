import os

def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html')])
    parts = []
    parts.append('<html><body><pre>')
    parts.append('<h1>os.environ:</h1>\n')
    for name, value in sorted(os.environ.items()):
        parts.append('%s=%s\n' % (name, value))
    parts.append('\n\n')
    parts.append('<h1>wsgi environ:</h1>\n')
    for name, value in sorted(os.environ.items()):
        if name.upper() != name:
            value = repr(value)
        parts.append('%s=%s\n' % (name, value))
    parts.append('</pre></body></html>')
    return parts
