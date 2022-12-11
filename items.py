# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


from scrapy.item import Item, Field


class TuoitreItem(Item):
    title = Field()
    content = Field()
    date = Field()
    category = Field()
    url = Field()
    image_urls = Field()
    image = Field()
