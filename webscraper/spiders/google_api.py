# -*- coding: utf-8 -*-
import scrapy

from urllib.parse import urlencode
import json
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class GoogleApiSpider(scrapy.Spider):
    name = 'google_api'
    allowed_domains = ['www.googleapis.com']

    handle_httpstatus_list = [400, 401, 403, 404, 405, 413, 500]

    def __init__(self, query='', limit=10, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super().__init__(**kwargs)

    def start_requests(self):
        key = self.settings.get('GOOGLE_API_KEY')
        cx = self.settings.get('GOOGLE_CSE_ID')
        base_url = 'https://www.googleapis.com/customsearch/v1?'
        payload = {'alt': 'json', 'prettyPrint': 'false', 'key': key, 'cx': cx, 'q': self.query}
        self.url = base_url + urlencode(payload)
        self.start_index = 0
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # Errors
        if (response.status >= 400):
            if response.status == 400:
                self.logger.warning('Bad request - The request has syntax error')
            elif response.status == 401:
                self.logger.warning('Authorization failure')
            elif response.status == 403:
                self.logger.warning('Forbidden - Daily limit reached')
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
        if 'items' not in response_json:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response_json['items']:
            item = SearchResultItem()
            item['query'] = self.query
            item['url']   = result['link']
            item['title'] = result['title']
            yield item
        self.logger.info('Response parsing completed')

        # Parse next page information
        if 'nextPage' in response_json['queries']:
            self.start_index = response_json['queries']['nextPage'][0]['startIndex']
            self.logger.info('Next search index %d', self.start_index)
            # Check limit
            if self.start_index <= self.limit or self.limit <= 0:
                next_page   = '&start=%d' % (self.start_index)
                url_next_page = self.url + next_page
                yield scrapy.Request(url = url_next_page, callback = self.parse)
            else:
                self.logger.info('Reached the result limit')
        else:
            self.logger.info('Reached the end of results')

