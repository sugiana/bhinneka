# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Notebook(Item):
    url = Field()
    title = Field()
    description = Field()
    picture = Field()
    price = Field()
    processor = Field()
    memory = Field()
    storage = Field()
    graphic = Field()
    monitor = Field()
    resolution = Field()
