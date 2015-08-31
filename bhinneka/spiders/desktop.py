from bhinneka.items import Desktop
from .notebook import NotebookSpider

 
class DesktopSpider(NotebookSpider):
    name = 'desktop'
    specs = dict(
        processor=['Tipe Prosessor', 'Processor Onboard'],
        memory=['Memori Standar'],
        storage=['Kapasitas Penyimpanan', 'Hard Drive'],
        graphic=['Tipe Grafis', 'VGA Card'],
        monitor=['Ukuran Layar', 'Monitor'],
        resolution=['Resolusi Layar'])
    brands = ['acer', 'asus', 'dell', 'hp', 'lenovo']
    brand_url_tpl = '{b}/category/komputer___pc___desktop/brands/{n}.aspx'
    product_class = Desktop
