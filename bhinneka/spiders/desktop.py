from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from bhinneka.items import Desktop
from .tools import (
    v,
    get_key_values,
    get_images,
    )
 
BRANDS = ['acer', 'asus', 'dell', 'hp', 'lenovo']
URLS = []
for brand in BRANDS:
    url = 'http://www.bhinneka.com/category/desktop_computer/brands/%s.aspx' % brand
    URLS.append(url)


class DesktopSpider(CrawlSpider):
    name = 'desktop'
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
        i = Desktop()
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
            elif key in ['Kapasitas Penyimpanan', 'Hard Drive']:
                i['storage'] = values
            elif key in ['Tipe Grafis', 'VGA Card']:
                i['graphic'] = values
            elif key in ['Ukuran Layar', 'Monitor']:
                i['monitor'] = values
            elif key == 'Resolusi Layar':
                i['resolution'] = values
        yield i
