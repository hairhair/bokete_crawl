# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Odai(scrapy.Item):
    number = scrapy.Field()
    img_src = scrapy.Field()
    top_boke = scrapy.Field()
    pass


class Boke(scrapy.Item):
    text = scrapy.Field()
    star = scrapy.Field()
    pass