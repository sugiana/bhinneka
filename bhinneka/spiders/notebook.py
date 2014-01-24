from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from bhinneka.items import Notebook
from .tools import (
    v,
    get_key_values,
    get_images,
    )
    
 
BRANDS = ['acer', 'apple', 'asus', 'axioo', 'dell', 'fujitsu', 'hp', 'lenovo',
          'sony', 'toshiba', 'samsung']
URLS = []
for brand in BRANDS:
    url = 'http://www.bhinneka.com/category/notebook___laptop/brands/%s.aspx/' % brand
    URLS.append(url)


class NotebookSpider(CrawlSpider):
    name = 'notebook'
    allowed_domains = ['bhinneka.com']
    start_urls = URLS
    rules = (
        Rule(SgmlLinkExtractor(
                restrict_xpaths=['//div[@id="products"]/table//tr'],
                allow=('\/products\/sku([\d]*)\/(.*)\.aspx$'),
                ),
              callback='parse_detail'),
        )

    def parse_detail(self, response):
        sel = Selector(response)
        i = Notebook()
        i['url'] = response.url
        i['title'] = v(sel.xpath('//h1[@itemprop="name"]/text()').extract())
        i['description'] = v(sel.xpath('//span[@id="ctl00_content_lblProductInformation"]/div/text()').extract())
        i['picture'] = get_images(sel, response.url)
        i['price'] = v(sel.xpath('//span[@itemprop="price"]/text()').extract())
        specs = sel.xpath('//span[@id="ctl00_content_lblDetail"]/table/tr')
        for spec in specs:
            cols = spec.xpath('td')
            key = v(cols[0].xpath('b/text()').extract())
            values = get_key_values(cols[1])
            if key in ('Tipe Prosessor', 'Processor Onboard'):
                i['processor'] = values
            elif key == 'Memori Standar':
                i['memory'] = values
            elif key == 'Kapasitas Penyimpanan':
                i['storage'] = values
            elif key == 'Tipe Grafis':
                i['graphic'] = values
            elif key == 'Ukuran Layar':
                i['monitor'] = values
            elif key == 'Resolusi Layar':
                i['resolution'] = values
            elif key == 'Baterai':
                i['battery'] = values
        yield i
