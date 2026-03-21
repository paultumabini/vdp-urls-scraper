import json
import math
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector

from ..items import ScrapebucketItem


class DealerdotcomSpider(scrapy.Spider):
    name = 'dealerdotcom'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
        'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:]).replace('-', '')

        # temporarily hardcoding condition:
        if self.domain_name.split('.')[0] == 'jimthompsonchrysler':
            yield scrapy.Request(
                url=f'{self.url}apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_NEW:inventory-data-bus1/getInventory?start=0',
                callback=self.parse,
            )

            yield scrapy.Request(
                url=f'{self.url}apis/widget/SITEBUILDER_USED_INVENTORY_1:inventory-data-bus1/getInventory?start=0',
                callback=self.parse,
            )

        else:

            for inventory in ['NEW', 'USED']:
                yield scrapy.Request(
                    url=f'{self.url}apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_{inventory}:inventory-data-bus1/getInventory?start=0',
                    meta={'inventory': inventory},
                    callback=self.parse,
                )

    def parse(self, response):
        # inventory = response.request.meta['inventory']
        json_res = json.loads(response.body)
        data = json_res.get('pageInfo').get('trackingData')

        total_units = json_res.get('pageInfo').get('totalCount')

        for vehicle_data in data:
            loader = ItemLoader(item=ScrapebucketItem())
            loader.add_value('category', vehicle_data.get('inventoryType'))
            loader.add_value('year', vehicle_data.get('modelYear'))
            loader.add_value('make', vehicle_data.get('make'))
            loader.add_value('model', vehicle_data.get('model'))
            loader.add_value('trim', vehicle_data.get('trim'))
            loader.add_value('stock_number', vehicle_data.get('stockNumber'))
            loader.add_value('vin', vehicle_data.get('vin'))
            loader.add_value('vehicle_url', f'{self.url}{vehicle_data.get("link")[1:]}')
            loader.add_value('msrp', vehicle_data.get('msrp'))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()

            total_units = json_res.get('pageInfo').get('totalCount')
            if total_units:
                units_per_page = 18
                number_of_pages = int(total_units / units_per_page)

                for page_start in range(1, number_of_pages + 1):

                    # temporarily hardcoding condition:
                    if self.domain_name.split('.')[0] == 'jimthompsonchrysler':
                        yield scrapy.Request(
                            url=f'{self.url}apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_NEW:inventory-data-bus1/getInventory?start={units_per_page * page_start}',
                            callback=self.parse,
                        )

                        yield scrapy.Request(
                            url=f'{self.url}apis/widget/SITEBUILDER_USED_INVENTORY_1:inventory-data-bus1/getInventory?start={units_per_page * page_start}',
                            callback=self.parse,
                        )
                    else:
                        for inventory in ['NEW', 'USED']:
                            yield scrapy.Request(
                                url=f'{self.url}apis/widget/INVENTORY_LISTING_DEFAULT_AUTO_{inventory}:inventory-data-bus1/getInventory?start={units_per_page * page_start}',
                                callback=self.parse,
                            )
