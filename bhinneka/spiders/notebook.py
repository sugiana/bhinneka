import os
from bhinneka.items import Notebook
from .tools import (
    CommonSpider,
    regex_compile,
    c_regex_search,
    clean,
    REGEX_UNITS,
    should_int,
    )


MEMORY_REGEXS = regex_compile([
    '(\d*) %s' % REGEX_UNITS, # 2 GB DDR-3
    '(\d*)%s' % REGEX_UNITS, # 8GB of 1600MHz LPDDR3 onboard memory
    ])

def parse_memory(values):
    for value in values:
        s = clean(value).lower()
        for rc in MEMORY_REGEXS:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            unit = match.group(2)
            return [value, int(amount), unit]
 
STORAGE_REGEXS = regex_compile([
    '(\d*) %s' % REGEX_UNITS, # 500 GB HDD
    '(\d*)%s' % REGEX_UNITS, # 256GB PCIe-based onboard flash storage
    ])

def parse_storage(values):
    for value in values:
        s = clean(value).lower()
        for rc in STORAGE_REGEXS:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            unit = match.group(2)
            return [value, int(amount), unit]
            
MONITOR_REGEXS = regex_compile([
    '(\d*\.\d) inch', # 12.5 inch
    '(\d*\.\d)"', # 12.5"
    '(\d*\.\d)" wxga', # 10.1" wxga
    '(\d*\.\d) wxga', # 10.1 wxga
    '(\d*)" wxga', # 12" wxga
    '(\d*) inch', # 12 inch
    '(\d*)"', # 12"
    '(\d*\.\d)', # 20.0 
    '(\d*)', # 20.0 
    ])
    
def parse_monitor(values):
    for value in values:
        s = clean(value).lower()
        for rc in MONITOR_REGEXS:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            if amount:
                return [value, should_int(float(amount))]

RESOLUTION_REGEXS = regex_compile([
    '(\d*)-by-(\d*)', # 2304-by-1440 resolution at 226 pixels per inch with support for millions of colors
    '(\d*) x (\d*)', # 1366 x 768
    '(\d*)x(\d*)', # 1920x1200
    ])

def parse_resolution(values):
    for value in values:
        s = clean(value).lower()
        for rc in RESOLUTION_REGEXS:
            match = c_regex_search(rc, s)
            if not match:
                continue
            count = len(match.groups())
            if count > 1:
                width = int(match.group(1))
                height = int(match.group(2))
                return [value, width, height]


class NotebookSpider(CommonSpider):
    name = 'notebook'
    start_urls = ['http://www.bhinneka.com/category/'\
                  'notebook___laptop_consumer.aspx']
    specs = dict(
        processor=('Tipe Prosessor', 'Processor Onboard'),
        memory=('Memori Standar',),
        storage=('Kapasitas Penyimpanan',),
        graphic=('Tipe Grafis',),
        monitor=('Ukuran Layar',),
        resolution=('Resolusi Layar',),
        battery=('Baterai',),
        operating_system=('Sistem Operasi',),
        )
    product_class = Notebook
    blacklist_brand_file = os.path.join('blacklist', 'brand', 'notebook.txt')    
    
    def parse_product(self, response):
        i = super(NotebookSpider, self).parse_product(response)
        if not i:
            return
        i = self.parse_memory(response, i)
        i = self.parse_storage(response, i)
        i = self.parse_monitor(response, i)
        i = self.parse_resolution(response, i)
        i = self.parse_graphic(response, i)
        i = self.parse_processor(response, i)
        i = self.parse_operating_system(response, i)
        i = self.parse_battery(response, i)
        return i
        
    def parse_memory(self, response, i):
        if 'memory' in i:
            vals = parse_memory(i['memory'])
            if vals:
                i['memory'] = vals
            else:
                del i['memory']
        return i
        
    def parse_storage(self, response, i):
        if 'storage' in i:
            vals = parse_storage(i['storage'])
            if vals:
                i['storage'] = vals
            else:
                del i['storage']
        return i        
        
    def parse_monitor(self, response, i):
        if 'monitor' in i:
            vals = parse_monitor(i['monitor'])
            if vals:
                i['monitor'] = vals
            else:
                del i['monitor']
        return i 
        
    def parse_resolution(self, response, i):
        if 'resolution' in i:
            vals = parse_resolution(i['resolution'])
            if vals:
                i['resolution'] = vals
            else:
                del i['resolution']
        return i
        
    def parse_graphic(self, response, i):
        if 'graphic' in i:
            i['graphic'] = i['graphic'][0]
        return i
        
    def parse_processor(self, response, i):
        if 'processor' in i:
            i['processor'] = i['processor'][0]
        return i
        
    def parse_operating_system(self, response, i):
        if 'operating_system' in i:
            i['operating_system'] = i['operating_system'][0]
        return i
        
    def parse_battery(self, response, i):
        if 'battery' in i:
            i['battery'] = i['battery'][0]
        return i
                       
