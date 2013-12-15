import re
import string
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from bhinneka.items import Notebook
from bhinneka.tools import clean, v

    
def harga(s):
    return int(s.lstrip('Rp ').replace(',', ''))
    
def get_key_values(c):
    r = []        
    for g in c.xpath('div/ul/li/i'):
        s = v(g.xpath('text()').extract())
        r.append(s)        
    if r:
        return r
    for g in c.xpath('div/ul/li'):
        s = v(g.xpath('text()').extract())
        r.append(s)
    if r:
        return r
    s = v(c.xpath('text()').extract())
    if s:
        return [s]        
    return r
    
def memori(values):
    regexs = [
        '([\d]*) (MB|GB|TB)',
        '([\d]*)(MB|GB|TB)',
        ]
    for value in values:
        s = clean(value)
        for regex in regexs:
            match = re.compile(regex).search(s)
            if match:
                nominal = int(match.group(1))
                satuan = match.group(2)
                return [s, nominal, satuan]
    raise Exception('Memori %s belum dipahami.' % values)

def layar(values):
    regexs = ['([\d]*\.[\d])&quot', '([\d]*\.[\d])"', '([\d]*)"']
    for value in values:
        s = clean(value)
        for regex in regexs:
            match = re.compile(regex).search(s)
            if match:
                nominal = float(match.group(1))
                return [s, nominal, 'inch']
    raise Exception('Ukuran layar %s belum dipahami.' % values)
    
def resolusi(values):
    regexs = ['([\d]*) x ([\d]*)', '([\d]*)x([\d]*)']
    for value in values:
        s = clean(value)
        for regex in regexs:
            match = re.compile(regex).search(s)
            if match:
                w = int(match.group(1))
                h = int(match.group(2))
                return [s, w, h]
    raise Exception('Resolusi layar %s belum dipahami.' % values)

def get_images(sel):
    images = sel.xpath('//div[@id="slider1"]/div/img')
    links = []
    for image in images:
        url = v(image.xpath('@src').extract())
        links.append(url)
    if links:
        return links
    images = sel.xpath('//img[@itemprop="image"]').xpath('@src').extract()
    if images:
        return [images[0]]
    raise Exception('Gambar tidak ada.')

     

class NotebookDetailSpider(CrawlSpider):
    name = 'notebook_detail'
    
    def __init__(self, path, *args, **kwargs):
        super(NotebookDetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['http://www.bhinneka.com' + path]

    def parse(self, response):
        sel = Selector(response)
        i = Notebook()
        i['url'] = self.start_urls[0]
        i['judul'] = v(sel.xpath('//h1[@itemprop="name"]/text()').extract())
        i['ringkasan'] = clean(v(sel.xpath('//span[@id="ctl00_content_lblProductInformation"]/div/text()').extract()))
        i['gambar'] = get_images(sel)
        i['harga'] = harga(v(sel.xpath('//span[@itemprop="price"]/text()').extract()))
        specs = sel.xpath('//span[@id="ctl00_content_lblDetail"]/table/tr')
        for spec in specs:
            cols = spec.xpath('td')
            key = v(cols[0].xpath('b/text()').extract())
            #value = v(cols[1].xpath('text()').extract())
            values = get_key_values(cols[1])
            if key == 'Tipe Prosessor':
                i['prosesor'] = clean(' '.join(values))
            elif key == 'Memori Standar':
                i['memori'] = memori(values)
            elif key == 'Kapasitas Penyimpanan':
                print('** %s' % cols[1].xpath('text()').extract())
                i['penyimpanan'] = memori(values)
            elif key == 'Tipe Grafis':
                i['grafik'] = values
            elif key == 'Ukuran Layar':
                i['layar'] = layar(values)
            elif key == 'Resolusi Layar':
                i['resolusi'] = resolusi(values)
        return i
