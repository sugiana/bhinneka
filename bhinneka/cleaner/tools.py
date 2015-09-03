import re
import string
from types import ListType
from bs4 import BeautifulSoup


##########
# String #
##########
def just_ascii(s):
    r = ''
    for ch in s:
        if ord(ch) > 127:
            ch = ' '
        r += ch
    return r

def clean_char(ch):
    if ch == u'\u201d':
        return '"'
    if ch == u'\xd7':
        return 'x'
    return ch in string.printable and ch or ' '

def one_space(s):
    while s.find('  ') > -1:
        s = s.replace('  ', ' ')
    return s
    
def clean(s):
    s = ''.join([clean_char(ch) for ch in s])
    s = one_space(s)
    if s.find('<span') < 0 and s.find('<br') < 0:
        return s
    soup = BeautifulSoup(s, 'lxml')
    for link in soup.find_all('span'):
        link.unwrap()
    s = str(soup).replace('<br/>', '\n').\
            lstrip('<html><body><p>').\
            rstrip('</p></body></html>')
    return s
    
def v(values):
    s = ' '.join(values)
    return s.strip()

######################
# Regular Expression #
######################
def regex_compile(regexs):
    r = []
    for regex in regexs:
        is_list = type(regex) == ListType
        if is_list:
            regex = regex[0]
        c = re.compile(regex)
        if is_list:
            c = [c] + regex[1:]
        r.append(c)
    return r
    
def c_regex_search(c_regex, text):
    return c_regex.search(text.lower())
    
def regex_search(regex, text):
    return re.compile(regex.lower()).search(text.lower())        
    

#########
# Price #
#########
def price(s):
    val = s.lower().replace('rp', 'idr').replace(',', '')
    if val:
        t = val.split()
        if len(t) != 2:
            return
        currency, amount = val.split()
        return [int(amount), currency]

##########
# Memory #
##########
UNITS = ['mb', 'gb', 'tb']
REGEX_UNITS = '(%s)' % '|'.join(UNITS)


TEXT_KEYS = ['brand', 'picture', 'description', 'title', 'url', 'battery',
             'graphic', 'processor']

def copy_text(data):
    r = dict()
    for key in TEXT_KEYS:
        if key in data:
            r[key] = data[key]
    if 'description' in r:
        r['description'] = clean(r['description'])
    return r

#################
# Error handler #
#################
def unknown_values(key, values):
    print('GAGAL menerjemahkan nilai dalam {k}:'.format(k=key))
    for value in values:
        print('  {v}'.format(v=[value]))
    #raise Exception('Tidak ditemukan pola yang cocok.')

def key_not_found(key, url):
    print('TIDAK ADA {k} di {u}'.format(k=key, u=url))
    
##########    
# Parser #
##########
def parse(keys, data, func):
    found = False
    first_key = keys[0]
    values = []
    for key in keys:
        if key not in data:
            continue
        value = data[key]
        found = True        
        if type(value) != ListType:
            value = [value]
        values += value
    if not found:
        for key in keys:
            key_not_found(key, data['url'])
        return
    val = func(values)
    if val is None:
        print('*** DEBUG parse_ {d}'.format(d=data))
        unknown_values(first_key, values)
    return val
    


