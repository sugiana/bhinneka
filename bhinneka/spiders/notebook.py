from bhinneka.items import Notebook
from .tools import CommonSpider
 

class NotebookSpider(CommonSpider):
    name = 'notebook'
    start_urls = ['http://www.bhinneka.com/category/notebook___laptop_consumer.aspx']
    specs = dict(
        processor=['Tipe Prosessor', 'Processor Onboard'],
        memory=['Memori Standar'],
        storage=['Kapasitas Penyimpanan'],
        graphic=['Tipe Grafis'],
        monitor=['Ukuran Layar'],
        resolution=['Resolusi Layar'],
        battery=['Baterai'],
        )
    product_class = Notebook
