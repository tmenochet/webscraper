# -*- coding: utf-8 -*-
import scrapy

from urllib.parse import urlencode
import re
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class GoogleWebSpider(scrapy.Spider):
    name = "google_web"
    allowed_domains = ['www.google.com']

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
    }
    handle_httpstatus_list = [302]

    NOTHING_MATCHES_TAG = (b'<div class="mnr-c">', b'did not match any documents.', b'Suggestions:')
    CAPTCHA_URL = b'https://www.google.com/sorry/index'

    def __init__(self, query='', limit=100, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super().__init__(**kwargs)

    def start_requests(self):
        base_url = 'https://www.google.com/search?'
        payload = {'num': 100, 'q': self.query}
        self.url = base_url + urlencode(payload)
        self.start_index = 0
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        # Errors
        if response.status == 302:
            if GoogleWebSpider.CAPTCHA_URL in response.headers['Location']:
               raise CloseSpider('Captcha redirect detected')
        if (response.status >= 400):
            raise CloseSpider('Error response returned')

        # Nothing found
        empty = True
        for tag in GoogleWebSpider.NOTHING_MATCHES_TAG:
            if tag not in response.body:
                empty = False
                break
        if empty:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response.css('h3.r'):
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
        current_page = response.css('td.cur::text').extract_first()
        if current_page:
            self.current_page = int(current_page)
            self.logger.info('Current search index %d', self.current_page)

        # Parse next page information
        next_page = response.css('a#pnnext::attr(href)').extract_first()
        if next_page:
            start_index = re.search('start=(\d+)', next_page, re.IGNORECASE).group(1)
            self.start_index = int(start_index)
            self.logger.info('Next search index %d', self.start_index)
            # Check limit
            if self.start_index < self.limit or self.limit <= 0:
                next_page = '&start=%d' % (self.start_index)
                url_next_page = self.url + next_page
                yield scrapy.Request(url = url_next_page, callback = self.parse)
            else:
                self.logger.info('Reached the result limit')
        else:
            self.logger.info('Reached the end of results')

