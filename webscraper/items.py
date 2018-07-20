# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WebscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SearchResultItem(scrapy.Item):
    query = scrapy.Field()
    url   = scrapy.Field()
    title = scrapy.Field()
    timestamp = scrapy.Field()
