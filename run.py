import os
import sys
import subprocess


def run(args):
    print(args)
    if subprocess.call(args) != 0:
        sys.exit()

def open_json(filename):
    f = open(filename)
    values = eval(f.read())
    f.close()
    return values

        
# http://stackoverflow.com/questions/7855794/how-can-i-create-a-seo-friendly-dash-delimited-url-from-a-string-in-python        
def seo_friendly(s, maxlen=64):
    t = '-'.join(s.split())
    u = ''.join([c for c in t if c.isalnum() or c=='-'])
    s = u[:maxlen].rstrip('-').lower()
    while s.find('--') > -1:
        s = s.replace('--', '-')
    return s
    
INVALID_PATH = [    
    '/products/sku01313611/hp_slatebook_10-h007ru_x2__e4x95pa_.aspx'
    ]

bin = '/home/sugiana/env/bin/scrapy'
#bin = 'scrapy'
list_file = 'notebook.json'
if not os.path.exists(list_file):
    run([bin, 'crawl', 'notebook', '-o', list_file, '-t', 'json'])

values = open_json(list_file)
for v in values:
    if v['url'] in INVALID_PATH:
        continue
    detail_file = seo_friendly(v['judul']) + '.json'
    if os.path.exists(detail_file) and os.stat(detail_file).st_size:
        continue
    run([bin, 'crawl', 'notebook_detail', '-a', 'path=' + v['url'], '-o', detail_file])
    file_info = os.stat(detail_file)
    if not file_info.st_size:
        print('File %s kosong.' % detail_file)
        sys.exit()
    vals = open_json(detail_file)
    if not vals['gambar']:
        print('Gambar kosong.')
        sys.exit()
    
os.remove(list_file)
