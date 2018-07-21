import os
from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from scrapy_wayback_machine import WaybackMachineMiddleware
from webscraper.items import SearchResultItem

class WaybackMachineSpider(CrawlSpider):
    name = 'waybackmachine'

    custom_settings = {
      'DOWNLOADER_MIDDLEWARES': {'scrapy_wayback_machine.WaybackMachineMiddleware':5}
    }
    handle_httpstatus_list = [404]

    def __init__(self, domain, *args, **kwargs):
        allow=()
        deny=()
        self.rules = (
            Rule(LinkExtractor(allow=allow, deny=deny), callback=self.parse_response),
        )

        # parse the allowed domains and start urls
        self.allowed_domains = []
        self.start_urls = []
        url_parts = domain.split('://')
        unqualified_url = url_parts[-1]
        url_scheme = url_parts[0] if len(url_parts) > 1 else 'http'
        full_url = '{0}://{1}'.format(url_scheme, unqualified_url)
        bare_domain = unqualified_url.split('/')[0]
        self.allowed_domains.append(bare_domain)
        self.start_urls.append(full_url)
        super().__init__(**kwargs)

    def parse_start_url(self, response):
        # scrapy doesn't call the callbacks for the start urls by default,
        # this overrides that behavior so that any matching callbacks are called
        for rule in self._rules:
            if rule.link_extractor._link_allowed(response):
                if rule.callback:
                    rule.callback(response)

    def parse_response(self, response):
        item = SearchResultItem()
        item['url'] = response.url
        time = response.meta['wayback_machine_time']
        item['timestamp'] = time.strftime(WaybackMachineMiddleware.timestamp_format)
        yield item
