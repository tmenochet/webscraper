# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import requests
import re
from scrapy.exceptions import DropItem

from scrapy import Request
from scrapy.pipelines.files import FilesPipeline

class WebscraperPipeline(object):
    def process_item(self, item, spider):
        return item

class BaiduWebPipeline(object):

    def open_spider(self, spider):
        self.pattern = re.compile(r"URL='(.*)'")

    def process_item(self, item, spider):
        if spider.name == 'baidu_web':
            try:
                old = item['url']
                res = requests.head(item['url'], allow_redirects=False)
                if res.status_code == 200:
                    matches = self.pattern.findall(res.text)
                    if matches:
                        item['url'] = matches[0]
                elif res.status_code in [301, 302]:
                    url = res.headers['location']
                    if url.startswith('http'):
                        item['url'] = url
            except Exception as e:
                print(e)

            if item['url'] == old:
                raise DropItem("Missing url in %s" % item)

        return item

class JsonWriterPipeline(object):

    def __init__(self):
        self.items_seen = set()

    def open_spider(self, spider):
        self.file = open(spider.name + '-items.jl', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if 'cache' in item:
            if (item['url'], item['cache']) in self.items_seen:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                self.items_seen.add((item['url'], item['cache']))
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line)
        return item

class ListWriterPipeline(object):

    def __init__(self):
        self.items_seen = set()

    def open_spider(self, spider):
        self.file = open(spider.name + '-items.lst', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        if 'status' in item and item['status'] == '404':
            raise DropItem("Item not found: %s" % item)
        elif item['url'] in self.items_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.items_seen.add(item['url'])
            line = dict(item)['url'] + '\n'
            self.file.write(line)
            return item

class FileDownloadPipeline(FilesPipeline):
    # Instantiate pipeline if FILES_STORE setting is specified
    @classmethod
    def from_crawler(cls, crawler):
        if 'FILES_STORE' in crawler.settings:
            pipe = cls.from_settings(crawler.settings)
            pipe.crawler = crawler
        else:
            pipe = None
        return pipe

    # Download file from item attribute 'url'
    def get_media_requests(self, item, info):
        yield Request(item.get('url'))

