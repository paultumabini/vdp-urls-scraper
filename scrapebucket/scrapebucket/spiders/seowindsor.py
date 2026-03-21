import json
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings

from ..items import ScrapebucketItem


class SeowindsorSpider(scrapy.Spider):
    name = 'seowindsor'
    # allowed_domains = []
    domain_name = ''

    custom_settings = {
        'DOWNLOAD_DELAY': 3,
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield scrapy.Request(
            url='https://darrylfrith.com/mkf/api/2022/api/inventory/0/NEW',
            callback=self.parse,
            headers={
                'User-Agent': get_project_settings().get('USER_AGENT'),
            },
        )
        yield scrapy.Request(
            url='https://darrylfrith.com/mkf/api/2022/api/inventory/0/USED',
            callback=self.parse,
            headers={
                'User-Agent': get_project_settings().get('USER_AGENT'),
            },
        )

    def parse(self, response):
        resp = json.loads(response.body)

        units = resp.get('results')

        for unit in units:

            loader = ItemLoader(item=ScrapebucketItem())
            loader.add_value('category', unit.get('condition'))
            loader.add_value('year', unit.get('year'))
            loader.add_value('make', unit.get('make'))
            loader.add_value('model', unit.get('model'))
            loader.add_value('trim', unit.get('trim'))
            loader.add_value('stock_number', unit.get('stock_id'))
            loader.add_value('vin', unit.get('vin'))
            loader.add_value('vehicle_url', f'{self.url}/inventory/listings/{unit.get("condition").lower()}?stockID={unit.get("stock_id")}')
            loader.add_value('price', unit.get('retail_price'))
            loader.add_value('selling_price', unit.get('sale_price'))
            loader.add_value(
                'image_urls', '|'.join([f'https://darrylfrith.com/mkf/api/uploadedImages/{url.get("image_key")}' for url in unit.get('images')])
            )
            loader.add_value('images_count', len(unit.get('images')))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()
