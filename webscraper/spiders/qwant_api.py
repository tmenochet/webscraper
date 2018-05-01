# -*- coding: utf-8 -*-
import scrapy

from urllib import urlencode
import json
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class QwantApiSpider(scrapy.Spider):
    name = "qwant_api"

    def __init__(self, query='', limit=10, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super(QwantApiSpider, self).__init__(*args, **kwargs)
        #super().__init__(**kwargs)  # python3

    def start_requests(self):
        base_url = 'https://api.qwant.com/api/search/web?'
        payload = {'count': 10, 'q': self.query}
        self.url = base_url + urlencode(payload)
        self.start_index = 0
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # Errors
        if (response.status != 200):
            self.logger.warning('Bad request')
            raise CloseSpider('Error response returned')

        response_json = json.loads(response.body_as_unicode())

        if 'error_code' in response_json['data']:
            self.logger.warning('Bad request')
            raise CloseSpider('Error response returned')

        # Nothing found
        if response_json['data']['result']['total'] == 0:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response_json['data']['result']['items']:
            item = SearchResultItem()
            item['url']   = result['url']
            item['title'] = result['title'].encode('utf-8')
            yield item
        self.logger.info('Response parsing completed')

        # Parse next page information
        if response_json['data']['query']['offset'] < response_json['data']['result']['total'] - 10:
            self.start_index = response_json['data']['query']['offset'] + 10
            self.logger.info('Next search index %d', self.start_index)
            # Check limit
            if self.start_index < self.limit or self.limit <= 0:
                next_page   = '&offset=%d' % (self.start_index)
                url_next_page = self.url + next_page
                yield scrapy.Request(url = url_next_page, callback = self.parse)
            else:
                self.logger.info('Reached the result limit')
        else:
            self.logger.info('Reached the end of results')

