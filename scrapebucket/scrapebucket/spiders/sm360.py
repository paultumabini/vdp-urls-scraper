import json
from urllib.parse import urlparse

import _jsonnet
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem


class Sm360Spider(CrawlSpider):
    name = 'sm360'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
        # 'SPIDER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketSpiderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        for which in ['new', 'used', 'certified']:
            yield scrapy.Request(url=f'{self.url}/{which}-inventory')

    # vehicle urls
    link_extractor1 = LinkExtractor(
        restrict_xpaths=[
            '//div[@class="inventory-preview-bravo-section-title"]/a',
            '//div[@class="inventory-preview-alpha-section-title"]/a',
            '//div[@class="inventory-preview-bravo__infos-wrapper"]/a',
        ]
    )
    # pagination urls
    link_extractor2 = LinkExtractor(restrict_xpaths='//a[starts-with(@class, "pagination__page-button")]')

    rules = (
        Rule(
            link_extractor1,
            callback='parse_item',
            follow=True,
            process_request='meta_processor',
        ),
        Rule(
            link_extractor2,
            follow=True,
            process_request='meta_processor',
        ),
    )

    def meta_processor(self, request, response):
        request.meta['page'] = response.url
        return request

    def parse_item(self, response):
        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        page = response.meta['page']

        # select elements at <script> tags then convert json string to json object
        json_txt = response.xpath(
            'normalize-space(substring-before(substring-after((//script[contains(.,"vehicleDetails:")]/text())[last()],"vehicleDetails:"),"formVehicle"))'
        ).get()[:-1]
        json_dict = json.loads(_jsonnet.evaluate_snippet('snippet', json_txt))

        loader.add_value('category', json_dict.get('status'))
        loader.add_value('year', json_dict.get('year'))
        loader.add_value('make', json_dict.get('make'))
        loader.add_value('model', json_dict.get('model'))
        loader.add_value('trim', json_dict.get('trim'))
        loader.add_value('stock_number', json_dict.get('stockNumber'))
        loader.add_value('vin', json_dict.get('vin'))
        loader.add_value('vehicle_url', response.url)
        loader.add_value('msrp', json_dict.get('msrp'))

        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
