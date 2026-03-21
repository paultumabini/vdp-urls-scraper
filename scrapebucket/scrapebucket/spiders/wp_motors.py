from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings

from ..items import ScrapebucketItem
from ..spider_helpers.playwright_helper import PlaywrightHelper


class WpMotorsSpider(CrawlSpider):
    name = 'wp_motors'
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(
            urlparse(self.url).netloc.split('.')[-2:],
        )

        yield scrapy.Request(url=f'{self.url}inventory/')

    # vehicle urls
    extractor1 = LinkExtractor(restrict_xpaths='//div[@class="title heading-font"]/a')
    # pagination urls
    extractor2 = LinkExtractor(restrict_xpaths='//ul[@class="page-numbers"]/li/a[@class="page-numbers"]')

    rules = (
        Rule(extractor1, callback='parse_item', follow=True),
        Rule(extractor2, follow=True, process_request='set_user_agent'),
    )

    def set_user_agent(self, request, spiders):
        request.headers['User-Agent'] = get_project_settings().get('USER_AGENT')
        return request

    def parse_item(self, response):
        loader = ItemLoader(item=ScrapebucketItem(), selector=response)

        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('vin', '//td[contains(@class,"t-vin")]/text()')

        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
