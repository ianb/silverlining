import os
import zipfile
import time
from cStringIO import StringIO
import tempita

def render_files(**ns):
    script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    base_path = '/var/topp/build-files/build-%s.zip' % time.strftime('%Y-%m-%d')
    zip_buffer = StringIO()
    zip = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)
    for filename in os.listdir(script_dir):
        full_name = os.path.join(script_dir, filename)
        if os.path.isdir(full_name):
            continue
        fp = open(full_name)
        content = fp.read()
        fp.close()
        outname = filename
        if filename.endswith('.tmpl'):
            outname = os.path.splitext(filename)[0]
            template = tempita.Template(content, name=full_name)
            content = template.substitute(**ns)
        zip.writestr(outname, content)
    zip.close()
    return {base_path: zip_buffer.getvalue()}
