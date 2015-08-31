from scrapy import (
    Request,
    FormRequest,
    )
from bhinneka.items import Notebook
from .tools import (
    BASE_URL,
    meta_from_response,
    CommonSpider,
    )
    
 

class NotebookSpider(CommonSpider):
    name = 'notebook'
    specs = dict(
        processor=['Tipe Prosessor', 'Processor Onboard'],
        memory=['Memori Standar'],
        storage=['Kapasitas Penyimpanan'],
        graphic=['Tipe Grafis'],
        monitor=['Ukuran Layar'],
        resolution=['Resolusi Layar'],
        battery=['Baterai'],
        )
    brands = ['acer', 'apple', 'asus', 'axioo', 'dell', 'fujitsu', 'hp',
              'lenovo', 'sony', 'toshiba', 'samsung']
    brand_url_tpl = '{b}/category/notebook___laptop/brands/{n}.aspx'
    product_class = Notebook

    def start_requests(self): # override from Spider class
        for brand in self.brands:
            url = self.brand_url_tpl.format(b=BASE_URL, n=brand)
            meta = dict(brand=brand)
            yield Request(url, self.parse, meta=meta)

    def product_request(self, response, url): # override from CommonSpider class
        meta = meta_from_response(response)
        return FormRequest(url=url, callback=self.product_parser, meta=meta)

    def product_instance(self, response):
        i = self.product_class()
        i['brand'] = response.meta['brand']
        return i

    def next_page_request(self, response, selector):
        data = self.next_page_data(selector)
        meta = meta_from_response(response)
        return FormRequest(url=response.url, method='POST', formdata=data,
                           callback=self.parse, meta=meta)
