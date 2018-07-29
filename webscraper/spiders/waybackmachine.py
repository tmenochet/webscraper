# -*- coding: utf-8 -*-

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.sitemap import Sitemap
from urllib.parse import urlencode
import json
from six.moves.urllib.parse import urljoin
import re

from webscraper.items import SearchResultItem

class WaybackMachineSpider(scrapy.Spider):
    name = 'waybackmachine'
    allowed_domains = ['web.archive.org']

    def __init__(self, domain, *args, **kwargs):
        self.domain = domain
        self.snapshot_url_template = 'http://web.archive.org/web/{timestamp}id_/{original}'
        self.timestamp_format = '%Y%m%d%H%M%S'
        super().__init__(**kwargs)

    def start_requests(self):
        base_url = 'https://web.archive.org/cdx/search/cdx?'
        url = self.domain + '/*'
        payload = {'url': url, 'output': 'json', 'fl': 'timestamp,original,statuscode'}
        self.url = base_url + urlencode(payload)
        yield scrapy.Request(url=self.url, callback=self.parse_start_url)

    def parse_start_url(self, response):
        # Errors
        if (response.status != 200):
            raise CloseSpider('Bad response returned')

        response_json = json.loads(response.body_as_unicode())

        # Nothing found
        if len(response_json) < 2:
            raise CloseSpider('Empty search result')

        # Extact all of result
        keys, rows = response_json[0], response_json[1:]
        def build_dict(row):
            new_dict = {}
            for i, key in enumerate(keys):
                new_dict[key] = row[i]
            return new_dict
        snapshots = list(map(build_dict, rows))
        del rows

        regex_sitemap = re.compile(r".*sitemap[^/]*\.xml$")

        for snapshot in snapshots:
            snapshot_url = self.snapshot_url_template.format(**snapshot)
            item = SearchResultItem()
            item['cache'] = snapshot_url
            item['url'] = snapshot['original']
            item['status'] = snapshot['statuscode']
            yield item

            if snapshot['original'].endswith('/robots.txt') and snapshot['statuscode'] == '200':
                yield scrapy.Request(url=snapshot_url, callback=self.parse_robots)
            elif regex_sitemap.match(snapshot['original']) and snapshot['statuscode'] == '200':
                yield scrapy.Request(url=snapshot_url, callback=self.parse_sitemap)

    def parse_robots(self, response):
        # Errors
        if (response.status != 200):
            raise CloseSpider('Bad response returned')

        # Parse robots.txt
        base_url = response.url.split('id_/')[1]
        for line in response.text.splitlines():
            if line == '# Welcome to the Archive!':
                break
            elif line.lstrip().lower().startswith('sitemap:') or line.lstrip().lower().startswith('allow:') or line.lstrip().lower().startswith('disallow:'):
                url = line.split(':', 1)[1].strip()
                item = SearchResultItem()
                item['cache'] = response.url
                item['url'] = urljoin(base_url, url)
                yield item

    def parse_sitemap(self, response):
        # Errors
        if (response.status != 200):
            raise CloseSpider('Bad response returned')

        # Parse sitemap.xml
        sitemap = Sitemap(response.body)
        if sitemap.type == 'urlset' or sitemap.type == 'sitemapindex':
            for url in sitemap:
               item = SearchResultItem()
               item['url'] = url['loc']
               item['cache'] = response.url
               yield item
               # Also consider alternate URLs (xhtml:link rel="alternate")
               if 'alternate' in url:
                   for alt in url['alternate']:
                       item = SearchResultItem()
                       item['url'] = alt
                       item['cache'] = response.url
                       yield item

