# -*- coding: utf-8 -*-
import scrapy

from urllib.parse import urlencode
import re
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class BingWebSpider(scrapy.Spider):
    name = "bing_web"
    allowed_domains = ['www.bing.com']

    NOTHING_MATCHES_TAG = (b'<li class="b_no">', b'There are no results for')

    def __init__(self, query='', limit=50, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super().__init__(**kwargs)

    def start_requests(self):
        base_url = 'https://www.bing.com/search?'
        self.cookies = {'mkt': 'en-US', 'ui': 'en-US', 'SRCHHPGUSR':'NEWWND=0&ADLT=DEMOTE&NRSLT=50'}
        payload = {'q': self.query, 'go': 'Submit', 'count': 50}
        self.url = base_url + urlencode(payload) + '&first={0}'
        self.start_index = 0
        yield scrapy.Request(url=self.url.format(self.start_index), callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        # Errors
        if (response.status >= 400):
            raise CloseSpider('Error response returned')

        # Nothing found
        empty = True
        for tag in BingWebSpider.NOTHING_MATCHES_TAG:
            if tag not in response.body:
                empty = False
                break
        if empty:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response.css('li.b_algo'):
            try:
                item = SearchResultItem()
                item['query'] = self.query
                item['url'] = re.search('http[s]*://.+', result.css('a::attr(href)').extract_first()).group()
                item['title'] = result.css('a::text').extract_first() or result.css('a span::text')
                yield item
            except Exception as e:
                self.logger.error('An error occured when extract the item: ' + str(e))
        self.logger.info('Response parsing completed')

        # Parse current page information
        current_page = response.css('span#drvph::attr(data-url)').extract_first()
        if current_page:
            start_index = re.search('first=(\d+)', current_page, re.IGNORECASE).group(1)
            self.current_page = int(start_index)
            self.logger.info('Current search index %d', self.current_page)

        # Parse next page information
        next_page = response.css('a.sb_pagN::attr(href)').extract_first()
        if next_page:
            start_index = re.search('first=(\d+)', next_page, re.IGNORECASE).group(1)
            self.start_index = int(start_index)
            self.logger.info('Next search index %d', self.start_index)
            # Check limit
            if self.start_index <= self.limit or self.limit <= 0:
                next_page = '&first=%d' % (self.start_index)
                url_next_page = self.url.format(next_page)
                yield scrapy.Request(url = url_next_page, callback = self.parse)
            else:
                self.logger.info('Reached the result limit')
        else:
            self.logger.info('Reached the end of results')

