from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem
from ..spider_helpers.response_json import loads_response_body
from ..utils import COOKIE_NOVLANBROS, cookie_parser


class WebstagerSpider(scrapy.Spider):
    name = 'webstager'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543
        },
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
        res_json = loads_response_body(
            response.body, url=response.url, label=self.name
        )
        if not res_json:
            return

        inventory = res_json.get('inventory') or {}
        for result in inventory.get('results') or []:
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
            images = result.get('images') or []
            loader.add_value(
                'image_urls',
                [image.get('remote') for image in images if isinstance(image, dict)],
            )
            loader.add_value('images_count', len(images))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()
