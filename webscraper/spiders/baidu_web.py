# -*- coding: utf-8 -*-
import scrapy

from urllib import urlencode
import re
from webscraper.items import SearchResultItem
from scrapy.exceptions import CloseSpider

class BaiduWebSpider(scrapy.Spider):
    name = "baidu_web"

    NOTHING_MATCHES_TAG = ('<div class="content_none"><div class="nors">', )

    def __init__(self, query='', limit=10, *args, **kwargs):
        self.query = query
        self.limit = int(limit)
        super(BaiduWebSpider, self).__init__(*args, **kwargs)
        #super().__init__(**kwargs)  # python3

    def start_requests(self):
        base_url = 'https://www.baidu.com/s?'
        payload = {'rn': 50, 'wd': self.query}
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
        for tag in BaiduWebSpider.NOTHING_MATCHES_TAG:
            if tag not in response.body:
                empty = False
                break
        if empty:
            raise CloseSpider('Empty search result')

        # Extact all of result
        for result in response.css('div.result > h3.t'):
            try:
                item = SearchResultItem()
                item['url'] = re.search('http[s]*://.+', result.css('a::attr(href)').extract_first()).group()
                title = u''.join([plain.extract() for plain in result.css('a::text')])
                item['title'] = title.encode('utf-8')
                yield item
            except Exception as e:
                self.logger.error('An error occured when extract the item: ' + str(e))
        self.logger.info('Response parsing completed')

        # Parse current page information
        current_page = response.css('strong > span.pc::text').extract_first()
        if current_page:
            self.current_page = int(current_page)
            self.logger.info('Current search index %d', self.current_page)

        # Parse next page information
        next_page = response.css('a.n::attr(href)').extract()
        next_text = response.css('a.n::text').extract()
        if next_page:
            length = len(next_page)
            # Stopped sending request if not next page button present
            if length > 1 or '>' in next_text[0]:
                if length == 2:
                    _, next_page = next_page
                else:
                    next_page = next_page[0]
                start_index = re.search(r'pn=(\d+)', next_page, re.IGNORECASE).group(1)
                self.start_index = int(start_index)
                self.logger.info('Next search index %d', self.start_index)
                # Check limit
                if self.start_index < self.limit or self.limit <= 0:
                    next_page = '&pn=%d' % (self.start_index)
                    url_next_page = self.url + next_page
                    yield scrapy.Request(url = url_next_page, callback = self.parse)
                else:
                    self.logger.info('Reached the result limit')
            else:
                self.logger.info('Reached the end of results')
        else:
            self.logger.info('Reached the end of results')

