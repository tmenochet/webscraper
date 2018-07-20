# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import requests
import re
from scrapy.exceptions import DropItem

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

    def open_spider(self, spider):
        self.file = open(spider.name + '-items.jl', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class ListWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open(spider.name + '-items.lst', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = dict(item)['url'] + "\n"
        self.file.write(line)
        return item

