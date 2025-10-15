import os
import glob
import re


HTML_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs', '_build', '**', '*.html')

print('Inverting HTML page titles in files:')
for p in glob.glob(HTML_PATH, recursive=True):
    print(p)
    with open(p, mode='r', encoding='utf-8') as f:
        data = f.read()
    data = re.sub(r'\<title\>(.*) &mdash; (.*)\<\/title\>', r'<title>\2 &mdash; \1</title>', data)
    with open(p, mode="w", encoding='utf-8') as f:
        f.write(data)
