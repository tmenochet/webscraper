# -*- coding: utf-8 -*-
import scrapy

from urllib import urlencode
import re
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class GoogleWebSpider(scrapy.Spider):
    name = "google_web"

    NOTHING_MATCHES_TAG = ('<div class="mnr-c">', 'did not match any documents.', 'Suggestions:')
    CAPTCHA_URL = 'https://ipv4.google.com/sorry/index'

    def __init__(self, query='', limit=10, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super(GoogleWebSpider, self).__init__(*args, **kwargs)
        #super().__init__(**kwargs)  # python3

    def start_requests(self):
        base_url = 'https://www.google.com/search?'
        payload = {'num': 100, 'q': self.query}
        self.url = base_url + urlencode(payload)
        self.start_index = 0
        yield scrapy.Request(url=self.url, callback=self.parse)

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

        # Nothing found
        empty = True
        for tag in GoogleWebSpider.NOTHING_MATCHES_TAG:
            if tag not in response.body:
                empty = False
                break
        if empty:
            raise CloseSpider('Empty search result')

        # Determine whether the captcha present
        if response.status in [301, 302]:
            if GoogleWebSpider.CAPTCHA_URL in response.headers['Location']:
               raise CloseSpider('Captcha redirect detected')

        # Extact all of result
        for result in response.css('h3.r'):
            try:
                item = SearchResultItem()
                item['url'] = re.search('http[s]*://.+', result.css('a::attr(href)').extract_first()).group()
                title = result.css('a::text').extract_first() or result.css('a span::text')
                #if not title:
                #    title = ''
                #item['title'] = title.encode('utf-8')
                item['title'] = title
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

