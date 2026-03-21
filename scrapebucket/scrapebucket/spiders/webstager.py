import json
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem
from ..utils import COOKIE_NOVLANBROS, cookie_parser


class WebstagerSpider(scrapy.Spider):
    name = 'webstager'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield scrapy.FormRequest(
            url=f'{self.url}inventory/',
            method='POST',
            cookies=cookie_parser(COOKIE_NOVLANBROS),
            headers={'Referer': f'{self.url}inventory/'},
            formdata={'actionList': 'search'},
        )

    def parse(self, response):
        res_json = json.loads(response.body)
        for result in res_json.get('inventory').get('results'):
            loader = ItemLoader(ScrapebucketItem())
            loader.add_value('category', result.get('url'))
            loader.add_value('year', result.get('year'))
            loader.add_value('make', result.get('make'))
            loader.add_value('model', result.get('model'))
            loader.add_value('trim', result.get('trim'))
            loader.add_value('unit', result.get('title'))
            loader.add_value('stock_number', result.get('stockNumber'))
            loader.add_value('vin', result.get('VIN'))
            loader.add_value('vehicle_url', result.get('url'))
            loader.add_value('msrp', result.get('msrp_price'))
            loader.add_value('price', result.get('price'))
            loader.add_value('image_urls', [image.get('remote') for image in result.get('images')])
            loader.add_value('images_count', len(result.get('images')))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()
