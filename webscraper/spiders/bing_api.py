# -*- coding: utf-8 -*-
import scrapy

from urllib.parse import urlencode
import json
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class BingApiSpider(scrapy.Spider):
    name = "bing_api"
    allowed_domains = ['api.cognitive.microsoft.com']

    handle_httpstatus_list = [400, 401, 403, 404, 405, 413, 500]

    def __init__(self, query='', limit=50, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super().__init__(**kwargs)

    def start_requests(self):
        key = self.settings.get('BING_API_KEY')
        base_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search?'
        payload = {'q': self.query, 'count': 50, 'responseFilter': 'WebPages'}
        self.headers = {'Ocp-Apim-Subscription-Key': key}
        self.url = base_url + urlencode(payload)
        self.start_index = 0
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        # Errors
        if (response.status >= 400):
            if response.status == 400:
                self.logger.warning('Bad request')
            elif response.status == 401:
                self.logger.warning('Authorization failure')
            elif response.status == 403:
                self.logger.warning('Forbidden')
            elif response.status == 404:
                self.logger.warning('Resource not found')
            elif response.status == 405:
                self.logger.warning('Method not allowed')
            elif response.status == 413:
                self.logger.warning('File too large')
            elif response.status == 500:
                self.logger.warning('Server error')
            raise CloseSpider('Error response returned')

        response_json = json.loads(response.body_as_unicode())

        # Nothing found
        if 'webPages' not in response_json:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response_json['webPages']['value']:
            item = SearchResultItem()
            item['query'] = self.query
            item['url']   = result['url']
            item['title'] = result['name']
            self.start_index += 1
            yield item
        self.logger.info('Response parsing completed')

        # Parse next page information
        if int(response_json['webPages']['totalEstimatedMatches']) - self.start_index > 0:
            self.logger.info('Next search index %d', self.start_index)
            # Check limit
            if self.start_index < self.limit or self.limit <= 0:
                next_page   = '&offset=%d' % (self.start_index)
                url_next_page = self.url + next_page
                yield scrapy.Request(url = url_next_page, headers = self.headers, callback = self.parse)
            else:
                self.logger.info('Reached the result limit')
        else:
            self.logger.info('Reached the end of results')

