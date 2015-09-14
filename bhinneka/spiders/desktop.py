from bhinneka.items import Desktop
from .notebook import NotebookSpider


class DesktopSpider(NotebookSpider):
    name = 'desktop'
    start_urls = ['http://www.bhinneka.com/category/'\
                  'komputer___pc___desktop.aspx']
    specs = dict(
        processor=('Tipe Prosessor', 'Processor Onboard'),
        memory=('Memori Standar',),
        storage=('Kapasitas Penyimpanan', 'Hard Drive'),
        graphic=('Tipe Grafis', 'VGA Card'),
        monitor=('Ukuran Layar', 'Monitor'),
        resolution=('Resolusi Layar',))
    product_class = Desktop
