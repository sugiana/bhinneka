from bhinneka.items import MobilePhone
from .tools import CommonSpider

    
class MobilePhoneSpider(CommonSpider):
    name = 'mobile_phone'
    start_urls = ['http://www.bhinneka.com/category/smart_phone_android.aspx']
    specs = dict(
        processor=['Tipe Prosessor', 'Kecepatan Prosessor'],
        memory=['Memori Internal'],
        battery=['Kapasitas Baterai'],
        monitor=['Ukuran Layar'],
        resolution=['Resolusi Layar'],
        camera=['Kamera'],
        operating_system=['Sistem Operasi'],
        )
    product_class = MobilePhone
