import json
import math
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector

from ..items import ScrapebucketItem


class FoxdealerSpider(scrapy.Spider):
    name = 'foxdealer'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
        'DOWNLOAD_DELAY': 1,
        # 'SPIDER_MIDDLEWARES': {
        #     'scrapebucket.middlewares.ScrapebucketSpiderMiddleware': 543,
        # },
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:]).replace('-', '')

        for category in ['new', 'used']:
            yield scrapy.Request(
                url=f'{self.url}api/ajax_requests/?currentQuery={self.url}inventory/{category}-page-1/',
                callback=self.parse,
            )

    def parse(self, response):
        # inventory = response.request.meta['inventory']
        json_res = json.loads(response.body)
        total_units = json_res.get('found_posts')
        posts = json_res.get('posts')

        for vehicle_data in posts:
            loader = ItemLoader(item=ScrapebucketItem())

            conditions = {
                'New': vehicle_data.get('is_new'),
                'Used': vehicle_data.get('is_used'),
            }

            condition = None

            for key, value in conditions.items():
                if value:
                    condition = key
            images = [img.get('url') for img in vehicle_data.get('imagelist')]

            loader.add_value('category', condition)
            loader.add_value('year', vehicle_data.get('year'))
            loader.add_value('make', vehicle_data.get('make'))
            loader.add_value('model', vehicle_data.get('model'))
            loader.add_value('trim', vehicle_data.get('trim'))
            loader.add_value('stock_number', vehicle_data.get('stock'))
            loader.add_value('vin', vehicle_data.get('vin'))
            loader.add_value('vehicle_url', f'{self.url}{vehicle_data.get("permalink")[1:]}')
            loader.add_value('msrp', vehicle_data.get('msrp'))
            loader.add_value('image_urls', images)
            loader.add_value('images_count', len(images))
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()

            page_links = json_res.get('page_links')

            if page_links:
                categories = ['New', 'Used']
                current_query = json_res.get('current_query')
                total_pages = int(Selector(text=page_links[-2]).xpath('//a/text()').get())
                category = ''

                for cat in categories:
                    if cat in current_query:
                        category = cat

                for next_page in range(2, total_pages + 1):
                    yield scrapy.Request(
                        url=f'{self.url}api/ajax_requests/?currentQuery={self.url}inventory/{category}-page-{next_page}/',
                        callback=self.parse,
                    )
