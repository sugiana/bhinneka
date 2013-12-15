from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from bhinneka.items import BhinnekaItem
from bhinneka.tools import v


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

    def parse(self, response):
        sel = Selector(response)
        items = []
        for row in sel.xpath('//div[@id="products"]/table/tr')[1:]:
            i = BhinnekaItem()        
            cols = row.xpath('td')
            if not cols[1:]:
                continue
            col = cols[1]
            i['url'] = v(col.xpath('a/@href').extract())
            i['judul'] = v(col.xpath('a/img/@title').extract())
            items.append(i)
        return items
