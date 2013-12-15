# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class BhinnekaItem(Item):
    # define the fields for your item here like:
    judul = Field()
    url = Field()


class Notebook(Item):
    judul = Field()
    url = Field()
    ringkasan = Field()
    gambar = Field()
    harga = Field()
    prosesor = Field()
    memori = Field()
    penyimpanan = Field()
    grafik = Field()
    layar = Field()
    resolusi = Field()
