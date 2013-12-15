import string


def clean_char(ch):
    if ch == u'\u201d':
        return '"'
    return ch in string.printable and ch or ' '

def one_space(s):
    while s.find('  ') > -1:
        s = s.replace('  ', ' ')
    return s
    
def clean(s):
    s = ''.join([clean_char(ch) for ch in s])
    return one_space(s)
    
def v(values):
    s = ' '.join(values)
    return s.strip()
    
def harga(s):
    return int(s.lstrip('Rp ').replace(',', ''))
