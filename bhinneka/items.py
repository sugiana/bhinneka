# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import (
    Item,
    Field,
    )


class Base(Item):
    url = Field()
    title = Field()
    description = Field()
    picture = Field()
    price = Field()
    brand = Field()
    model = Field()

class Computer(Base):
    processor = Field()
    memory = Field()
    storage = Field()
    graphic = Field()
    operating_system = Field()
    
class Desktop(Computer):
    monitor = Field()
    resolution = Field()    

class Notebook(Desktop):
    battery = Field()
    
class MobilePhone(Notebook):
    camera = Field()
    front_camera = Field()
