import re
import string
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from bhinneka.items import Notebook
from bhinneka.tools import v, clean


def price(s):
    value = int(s.lstrip('Rp ').replace(',', ''))
    return s, value
    
def get_key_values(c):
    r = []        
    for g in c.xpath('div/ul/li/i'):
        s = v(g.xpath('text()').extract())
        r.append(s)        
    for g in c.xpath('div/ul/li'):
        s = v(g.xpath('text()').extract())
        r.append(s)
    s = v(c.xpath('text()').extract())
    if s:
        r.append(s)
    return r
 
MBs = dict(
        MB=1,
        GB=1024,
        TB=1024*1024,
        )
units = '|'.join(MBs.keys())
memory_regexs = [
    '(\d*) (%s)' % units,
    '(\d*)(%s)' % units,
    ]

def memory(values, url):
    for value in values:
        s = clean(value)
        for regex in memory_regexs:
            match = re.compile(regex).search(s)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                mb = MBs[unit]
                amount = amount * mb
                return [s, amount]
    raise CloseSpider('%s: Unrecognize memory %s.' % (url, values))

regex_monitor = [
    '([\d]*\.[\d])&quot',
    '([\d]*\.[\d])"',
    '([\d]*)"',
    '([\d]*)&quot ',
    ]
    
def monitor(values, url):
    for value in values:
        s = clean(value)
        for regex in regex_monitor:
            match = re.compile(regex).search(s)
            if match:
                nominal = float(match.group(1))
                return [s, nominal] # inch
    raise CloseSpider('%s: Unrecognize monitor size %s.' % (url, values))
    
def resolution(values, url):
    regexs = ['([\d]*) x ([\d]*)', '([\d]*)x([\d]*)']
    for value in values:
        s = clean(value)
        for regex in regexs:
            match = re.compile(regex).search(s)
            if match:
                w = int(match.group(1))
                h = int(match.group(2))
                return [s, w, h]
    raise CloseSpider('%s: Unrecognize display resolution %s.' % (url, values))

def get_images(sel, url):
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
    raise CloseSpider('%s: Image not found.' % url)

 
BRANDS = ['acer', 'asus', 'dell', 'hp', 'lenovo']
URLS = []
for brand in BRANDS:
    url = 'http://www.bhinneka.com/category/desktop_computer/brands/%s.aspx' % brand
    URLS.append(url)


class NotebookSpider(CrawlSpider):
    name = 'desktop'
    allowed_domains = ['bhinneka.com']
    start_urls = URLS
    rules = (
        [Rule(SgmlLinkExtractor(
                restrict_xpaths=['//div[@id="products"]/table//tr'],
                allow=('\/products\/sku([\d]*)\/(.*)\.aspx$'),
                deny=(
                    # Invalid graphic card
                    #'http://www.bhinneka.com/products/sku01112984/asus_eeetop_1612iuts-b002f_all-in-one_-_black.aspx'
                )),
              callback='parse_detail'),
            ]
        )

    def parse_detail(self, response):
        sel = Selector(response)
        i = Notebook()
        i['url'] = response.url
        i['title'] = v(sel.xpath('//h1[@itemprop="name"]/text()').extract())
        i['description'] = clean(v(sel.xpath('//span[@id="ctl00_content_lblProductInformation"]/div/text()').extract()))
        i['picture'] = get_images(sel, response.url)
        i['price'] = price(v(sel.xpath('//span[@itemprop="price"]/text()').extract()))
        specs = sel.xpath('//span[@id="ctl00_content_lblDetail"]/table/tr')
        for spec in specs:
            cols = spec.xpath('td')
            key = v(cols[0].xpath('b/text()').extract())
            values = get_key_values(cols[1])
            if key in ('Tipe Prosessor', 'Processor Onboard'):
                i['processor'] = clean(' '.join(values))
            elif key == 'Memori Standar':
                i['memory'] = memory(values, response.url)
            elif key in ['Kapasitas Penyimpanan', 'Hard Drive']:
                i['storage'] = memory(values, response.url)
            elif key in ['Tipe Grafis', 'VGA Card']:
                i['graphic'] = values
            elif key in ['Ukuran Layar', 'Monitor']:
                i['monitor'] = monitor(values, response.url)
            elif key == 'Resolusi Layar':
                i['resolution'] = resolution(values, response.url)
        yield i
