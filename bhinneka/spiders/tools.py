import os
import re
import string
from glob import glob
from urlparse import urlsplit
from scrapy import (
    Request,
    FormRequest,
    )
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.exceptions import CloseSpider
from bs4 import BeautifulSoup


BASE_URL = 'http://www.bhinneka.com'


def v(values):
    s = ' '.join(values)
    return s.strip()
    
def one_space(s):
    while s.find('  ') > -1:
        s = s.replace('  ', ' ')
    return s
    
def clean_char(ch):
    if ch == u'\u201d':
        return '"'
    if ch == u'\xd7':
        return 'x'
    return ch in string.printable and ch or ' '        
    
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
 
def get_image(sel, url):
    images = sel.xpath('//div[@id="slider1"]/div/img')
    for image in images:
        return v(image.xpath('@src').extract())
    images = sel.xpath('//img[@itemprop="image"]').xpath('@src').extract()
    if images:
        return images[0]
    images = sel.xpath('//div[@id="prodMedia"]/div/img')
    if images:
        image = images[0]
        return v(image.xpath('@src').extract())

def meta_from_response(response):
    return dict(brand=response.meta['brand'])


def file_as_list(filename):
    if not os.path.exists(filename):
        return []
    s_list = []
    f = open(filename)
    for line in f.readlines():
        s = line.strip()
        s_list.append(s)
    f.close()
    return s_list

def is_url_local(url):
    return url.find('file://') > -1

def url2file(url):
    return url.replace('file://','').rstrip('/')
    
def is_url_local_file(url):
    if not is_url_local(url):
        return
    filename = url2file(url)
    return os.path.isfile(filename)

def get_start_urls(url):
    if not is_url_local(url):
        return [url]
    if is_url_local_file(url):
        return [url]
    dir_name = url2file(url)
    pattern = dir_name + '/*.aspx'
    r = []
    for filename in glob(pattern):
        url_local = 'file://' + filename
        r.append(url_local)
    return r    
    
def parse_url(sel):
    s = sel.xpath('//meta[@property="og:url"]').xpath('@content').extract()
    return v(s)
    
def parse_title(sel):    
    s = sel.xpath('//meta[@property="og:title"]').xpath('@content').extract()
    return v(s)
    
def parse_description(sel):    
    s = sel.xpath('//meta[@itemprop="description"]').xpath('@content').extract()
    s = v(s)
    s = s.replace('\r\n', ' ')
    return clean(s)
    
PRICE_TPL = '//div[@id="ctl00_content_divPrice"]/span[@itemprop="{i}"]'

def parse_price_(sel, itemprop):
    s = PRICE_TPL.format(i=itemprop)
    s = sel.xpath(s).xpath('@content').extract()
    return v(s)

def parse_price(sel):
    amount = parse_price_(sel, 'price')
    if not amount:
        return
    currency = parse_price_(sel, 'priceCurrency')
    if not currency:
        s = sel.extract()
        p = s.find('"Currency": "')
        if p > -1:
            currency = s[p+13:p+16] 
    s = ' '.join([currency, amount])
    return [s, int(amount), currency.lower()]
    
def parse_brand(sel):    
    s = sel.xpath('//a[@id="ctl00_content_lnkBrand"]').xpath('@title').extract()
    return v(s)    

def parse_model(sel):
    s = sel.xpath('//meta[@itemprop="model"]').xpath('@content').extract()
    return v(s)


class CommonSpider(Spider):
    allowed_domains = ('bhinneka.com',)
    start_page = None
    product_class = None # override please
    blacklist_brand_file = None
    
    def __init__(self, product_url=None, save_dir=None, *args, **kwargs):
        super(CommonSpider, self).__init__(*args, **kwargs)
        self.product_url = product_url
        self.save_dir = save_dir
        if product_url:
            self.start_urls = get_start_urls(product_url)
        self.blacklist_brand = self.blacklist_brand_file and \
            file_as_list(self.blacklist_brand_file) or []            

    # Override from parent class
    def parse(self, response):
        if self.product_url:
            yield self.parse_product(response)
            return    
        xs = Selector(response)
        for url in xs.xpath('//a[@class="prod-itm-link"]').re('href="(.*)"'):
            url_ = BASE_URL + url
            yield self.product_request(response, url_)
        xs_next = xs.xpath('//div[@id="divItemsPager"]')
        if not xs_next:
            return
        selector = Selector(text=xs_next.extract()[0])
        urls = selector.xpath('//a[@rel="Next"]').xpath('@href').extract()
        if urls:
            url = BASE_URL + urls[0]
            yield Request(url=url)

    def product_request(self, response, url):
        return FormRequest(url=url, callback=self.parse_product_)

    def product_instance(self, response):
        return self.product_class()
        
    def parse_product_(self, response):
        yield self.parse_product(response)        

    def parse_product(self, response):
        if self.save_dir:
            self.save(response)    
        sel = Selector(response)
        i = self.product_instance(response)        
        i = self.parse_brand(response, sel, i)        
        if self.is_blacklist(response, i):
            return        
        i = self.parse_url(response, sel, i)
        i = self.parse_title(response, sel, i)
        i = self.parse_description(response, sel, i)
        i = self.parse_picture(response, sel, i)
        i = self.parse_price(response, sel, i)
        i = self.parse_model(response, sel, i)
        specs = sel.xpath('//table[@class="spesifications"]/tr')
        for spec in specs:
            cols = spec.xpath('td')
            key = v(cols[0].xpath('b/text()').extract())
            values = get_key_values(cols[1])
            for spec_name in self.specs:
                spec_vals = self.specs[spec_name]
                if key in spec_vals:
                    i[spec_name] = values
        return i
    
    def parse_url(self, response, sel, i):
        s = parse_url(sel)
        if s:
            i['url'] = s
        return i

    def parse_title(self, response, sel, i):
        s = parse_title(sel)
        if s:
            i['title'] = s
        return i
        
    def parse_description(self, response, sel, i):
        s = parse_description(sel)
        if s:
            i['description'] = s
        return i
        
    def parse_picture(self, response, sel, i):
        image = get_image(sel, response.url)
        if image:
            i['picture'] = image
        return i
                    
    def parse_price(self, response, sel, i):
        price = parse_price(sel)
        if price:
            i['price'] = price
        return i
        
    def parse_brand(self, response, sel, i):
        brand = parse_brand(sel)
        if brand:
            i['brand'] = brand
        return i
        
    def parse_model(self, response, sel, i):
        model = parse_model(sel)
        if model:
            i['model'] = model
        return i 
        
    def save(self, response):
        u = urlsplit(response.url)
        filename = os.path.split(u.path)[-1]
        fullpath = os.path.join(self.save_dir, filename)
        f = open(fullpath, 'w')
        f.write(response.body)
        f.close()        
        
    def is_blacklist(self, response, data):
        if 'brand' in data:
            b = data['brand'].strip().lower()
            if b in self.blacklist_brand:
                self.logger.info('{url} brand {b} di-blacklist.'.\
                    format(url=response.url, b=b))
                return True
                        
        
######################
# Regular Expression #
######################
def regex_compile(regexs):
    r = []
    for regex in regexs:
        c = re.compile(regex)
        r.append(c)
    return r
    
def c_regex_search(c_regex, text):
    return c_regex.search(text.lower())

# Saat ambil nilai dari sumber teks bebas seperti description maka salin
# teks yang dimaksud seperlunya saja, jangan keseluruhan description.    
def regex_get_original_words(pattern, str_lower, str_orig):
    pattern = '({s})'.format(s=pattern)
    match = re.compile(pattern).search(str_lower)
    found = match.group(1)
    p = str_lower.find(found)
    return str_orig[p:p+len(found)]
    
##########
# Memory #
##########
UNITS = ['mb', 'gb', 'tb']
REGEX_UNITS = '(%s)' % '|'.join(UNITS)    

###########
# Numeric #
###########    
def should_int(value):
    int_ = int(value)
    return int_ == value and int_ or value
