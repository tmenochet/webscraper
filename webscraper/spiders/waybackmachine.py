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
            Rule(LinkExtractor(allow=allow, deny=deny), callback=self.parse),
        )

        # parse the allowed domains and start urls
        self.allowed_domains = []
        self.start_urls = []
        url = 'http://' + domain + '/*'
        self.allowed_domains.append(domain)
        self.start_urls.append(url)

        super().__init__()

    def parse_start_url(self, response):
        # scrapy doesn't call the callbacks for the start urls by default,
        # this overrides that behavior so that any matching callbacks are called
        for rule in self._rules:
            if rule.link_extractor._link_allowed(response):
                if rule.callback:
                    rule.callback(response)

    def parse(self, response):
        item = SearchResultItem()
        item['url'] = response.meta['wayback_machine_url'].split("id_/")[1]
        time = response.meta['wayback_machine_time']
        item['timestamp'] = time.strftime(WaybackMachineMiddleware.timestamp_format)
        yield item
