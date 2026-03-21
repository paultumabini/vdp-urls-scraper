import json
from urllib.parse import urlparse

import requests
import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem


class NabthatSpider(scrapy.Spider):
    name = 'nabthat'
    # allowed_domains = []
    domain_name = ''

    custom_settings = {
        # 'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543
        },
        # 'ITEM_PIPELINES': {'scrapebucket.pipelines.NabthatPipeline': 300},
    }

    def start_requests(self):

        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield scrapy.Request(
            url=f'{self.url}api/v1/vehicles?category=new&order=in_stock_date_desc&page=1',
            callback=self.parse,
        )
        yield scrapy.Request(
            url=f'{self.url}api/v1/vehicles?category=used&order=price_asc&page=1',
            callback=self.parse,
        )

    def get_image_urls(self, vin):
        response = requests.get(url=f'{self.url}/api/v1/vehicles/{vin}')
        data = response.json()
        image_urls = data.get('vehicle').get('images')
        return image_urls

    def parse(self, response):
        resp = json.loads(response.body)
        units = resp.get('models')

        for unit in units:
            images = [url.get('href') for url in self.get_image_urls(unit.get('vin'))]

            loader = ItemLoader(item=ScrapebucketItem())
            loader.add_value('vin', unit.get('vin'))
            loader.add_value('vehicle_url', unit.get('vehicle_url'))
            loader.add_value('category', unit.get('category'))
            loader.add_value('year', unit.get('year'))
            loader.add_value('make', unit.get('make'))
            loader.add_value('model', unit.get('model'))
            loader.add_value('trim', unit.get('trim'))
            loader.add_value('stock_number', unit.get('stock'))
            loader.add_value('msrp', unit.get('pricing').get('msrp'))
            loader.add_value('price', unit.get('pricing').get('price'))
            loader.add_value('selling_price', unit.get('pricing').get('selling_price'))
            loader.add_value('image_urls', images)
            loader.add_value('images_count', len(images))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()

        has_next = resp.get('meta').get('nextPage')
        if has_next:
            yield scrapy.Request(
                url=f'{self.url}/api/v1/vehicles?category=new&order=in_stock_date_desc&page={has_next}',
                callback=self.parse,
            )
            yield scrapy.Request(
                url=f'{self.url}/api/v1/vehicles?category=used&order=price_asc&page={has_next}',
                callback=self.parse,
            )
