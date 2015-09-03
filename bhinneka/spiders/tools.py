from scrapy import (
    Request,
    FormRequest,
    )
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy.exceptions import CloseSpider


BASE_URL = 'http://www.bhinneka.com'
XPATH_NEXT_PAGE = '//a[@id="ctl00_content_listViewItemPagerBottom_'\
                  'pagerNext_lbNext"]'
EVENTTARGET = 'ctl00$content$listViewItemsPager$pagerNext$lbNext'
EVENTTARGET_PAGE_TPL = 'ctl00$content$listViewItemsPager$pager{page}'\
                       '$lbNumericPager'



def v(values):
    s = ' '.join(values)
    return s.strip()

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
    images = sel.xpath('//div[@id="prodMedia"]/div/img')
    if images:
        image = images[0]
        return [v(image.xpath('@src').extract())]
    raise CloseSpider('{u}: Image not found.'.format(u=url))

def meta_from_response(response):
    return dict(brand=response.meta['brand'])


class CommonSpider(Spider):
    allowed_domains = ['bhinneka.com']
    start_page = None
    product_class = None # override please

    def parse(self, response): # override from Spider class
        xs = Selector(response)
        if self.start_page and 'start_page' not in response.meta:
            yield self.goto_page_request(response, xs)
        else:
            for url in xs.xpath('//a[@class="prod-itm-link"]').re('href="(.*)"'):
                url_ = BASE_URL + url
                yield self.product_request(response, url_)
            if xs.xpath(XPATH_NEXT_PAGE).extract():
                yield self.next_page_request(response, xs) 

    def next_page_data(self, selector):
        data = self._form_data(selector)
        data['__EVENTTARGET'] = EVENTTARGET
        return data

    def goto_page_data(self, selector):
        data = self._form_data(selector)
        data['__EVENTTARGET'] = EVENTTARGET_PAGE_TPL.format(
                                    page=self.start_page)
        return data

    def _form_data(self, selector):
        data = dict() 
        for sel_input in selector.xpath('//input[@type="hidden"]'):
            n = sel_input.xpath('@name').extract()
            if not n:
                continue
            n = n[0]
            if n in data:
                continue
            v = sel_input.xpath('@value').extract()
            if not v:
                continue
            v = v[0]
            data[n] = v
        return data

    def next_page_request(self, response, selector):
        data = self.next_page_data(selector)
        return FormRequest(url=response.url, method='POST', formdata=data,
                          callback=self.parse)

    def goto_page_request(self, response, selector):
        data = self.goto_page_data(selector)
        meta = dict(start_page=self.start_page)
        return FormRequest(url=response.url, method='POST', formdata=data,
                           callback=self.parse, meta=meta)

    def product_request(self, response, url):
        return FormRequest(url=url, callback=self.product_parser)

    def product_instance(self, response):
        return self.product_class()

    def product_parser(self, response):
        sel = Selector(response)
        i = self.product_instance(response)
        i['url'] = response.url
        i['title'] = v(sel.xpath('//h1[@itemprop="name"]/text()').extract())
        i['description'] = v(sel.xpath('//meta[@itemprop="description"]').\
                             xpath('@content').extract())
        i['picture'] = get_images(sel, response.url)
        i['price'] = v(sel.xpath('//span[@itemprop="price"]/text()').extract())
        i['brand'] = v(sel.xpath('//a[@id="ctl00_content_lnkBrand"]').\
                        xpath('@title').extract())
        specs = sel.xpath('//table[@class="spesifications"]/tr')
        for spec in specs:
            cols = spec.xpath('td')
            key = v(cols[0].xpath('b/text()').extract())
            values = get_key_values(cols[1])
            for spec_name in self.specs:
                spec_vals = self.specs[spec_name]
                if key in spec_vals:
                    i[spec_name] = values
        yield i

    # Bisa dipanggil di start_requests() pasca perbaikan parser sehingga
    # tidak mulai dari awal.
    def test_product_request(self, url):
        return Request(url, self.product_parser)
