#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from time import sleep

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

from webscraper.spiders.waybackmachine import WaybackMachineSpider
from webscraper.spiders.google_web import GoogleWebSpider
from webscraper.spiders.google_api import GoogleApiSpider
from webscraper.spiders.qwant_api import QwantApiSpider
from webscraper.spiders.baidu_web import BaiduWebSpider
from webscraper.spiders.bing_web import BingWebSpider
from webscraper.spiders.bing_api import BingApiSpider

@defer.inlineCallbacks
def crawl(runner, args):
    if args.spider == 'waybackmachine':
        config = {
            'domain': args.domain,
        }
        yield runner.crawl(WaybackMachineSpider, **config)
    elif args.spider == 'google_web':
        with open('data/google_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s %s' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(GoogleWebSpider, **config)
    elif args.spider == 'google_api':
        with open('data/google_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s %s' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(GoogleApiSpider, **config)
    elif args.spider == 'bing_web':
        with open('data/bing_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s (%s)' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(BingWebSpider, **config)
    elif args.spider == 'bing_api':
        with open('data/bing_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s %s' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(BingApiSpider, **config)
    elif args.spider == 'qwant_api':
        with open('data/qwant_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s (%s)' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(QwantApiSpider, **config)
    elif args.spider == 'baidu_web':
        with open('data/qwant_dorks.txt', 'r') as fp:
            dorks = [x.strip() for x in fp.read().splitlines() if x and not x.startswith('#')]
        for dork in dorks:
            config = {
               'query': 'site:%s %s' % (args.domain, dork),
               'limit': args.limit
            }
            sleep(args.delay)
            yield runner.crawl(BaiduWebSpider, **config)
    reactor.stop()

def main():
    # configure the settings for the crawler and spider
    args = parse_args()
    settings = get_project_settings()
    settings.update({
        'LOG_LEVEL': 'DEBUG' if args.verbose else 'INFO',
        'DOWNLOAD_DELAY': args.delay,
        'WAYBACK_MACHINE_TIME_RANGE': (getattr(args, 'from'), args.to),
        'ITEM_PIPELINES': {
            'webscraper.pipelines.BaiduWebPipeline': 300,
            'webscraper.pipelines.JsonWriterPipeline': 400,
            'webscraper.pipelines.ListWriterPipeline': 500,
        }
    })

    # start the crawler
    configure_logging()
    runner = CrawlerRunner(settings)
    crawl(runner, args)
    reactor.run()

def parse_args():
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=formatter, description=(
        'Scrapes search engines to fetch juicy resources by leveraging dorks. '
        'Parses the URLs stored by mirrors to find unlinked and old pages.'
    ))
    parser.add_argument('-v', '--verbose', action='store_true', help=(
        'Turn on debug logging.'
    ))
    parser.add_argument('--delay', metavar='DELAY', default=0, type=int, help=(
        'Specify the delay between crawl requests.'))
    parser.add_argument('-s', '--spider', required=True, metavar='ENGINE', type=str, help=(
        'Specify the spider to use.'
    ))
    parser.add_argument('-d', '--domain', required=True, metavar='DOMAIN', type=str, help=(
        'Specify the domain(s) to scrape.'
    ))
    parser.add_argument('-l', '--limit', metavar='LIMIT', default=10, type=int, help=(
        'Specify the limit number of result to scrape by query.'
    ))
    parser.add_argument('-f', '--from', metavar='TIMESTAMP', default='10000101', help=(
        'The timestamp for the beginning of the range to scrape. '
        'Can either be YYYYmmdd, YYYYmmddHHMMSS, or a Unix timestamp.'
    ))
    parser.add_argument('-t', '--to', metavar='TIMESTAMP', default='30000101', help=(
        'The timestamp for the end of the range to scrape. '
        'Use the same timestamp as `--from` to specify a single point in time.'
    ))
    return parser.parse_args()

if __name__ == "__main__":
    main()
