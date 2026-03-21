import json
import math
from urllib.parse import urlparse

import requests
import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem
from ..spider_helpers.url_qs import access_trader_direct_API, get_company_id


class ConvertusSpider(scrapy.Spider):
    name = 'convertus'
    domain_name = ''
    page = 1

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543
        },
        # 'DOWNLOAD_DELAY': 3,
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        dn = self.domain_name.split('.')[0]

        # get company_id
        self.company_id = get_company_id(dn)
        # if feed_id not found
        if not self.company_id:
            return

        yield scrapy.Request(
            url=f'{access_trader_direct_API( self.company_id, self.page, 15)}',
            callback=self.parse,
        )

    def parse(self, response):
        json_res = json.loads(response.body)
        parsed_data = json_res.get('results')

        for result in parsed_data:
            loader = ItemLoader(ScrapebucketItem())

            # images = [image.get('image_original') for image in result.get('image', {})]

            vdp_url = result.get('vdp_url')
            indexed = vdp_url.index('vehicles/')
            new_vdp_url = self.url + vdp_url[indexed:]

            loader.add_value('category', result.get('sale_class'))
            loader.add_value('year', result.get('year'))
            loader.add_value('make', result.get('make'))
            loader.add_value('model', result.get('model'))
            loader.add_value('trim', result.get('trim'))
            loader.add_value('stock_number', result.get('stock_number'))
            loader.add_value('vin', result.get('vin'))
            loader.add_value('vehicle_url', new_vdp_url)
            loader.add_value('price', result.get('asking_price'))
            # loader.add_value('image_urls', images)
            # loader.add_value('images_count', len(images))
            loader.add_value('domain', self.domain_name)
            yield loader.load_item()

        # crawl following pages
        pages = json_res.get('summary').get('total_vehicles')
        page_limit = math.ceil(pages / 15)

        if self.page <= page_limit:
            self.page += 1
            yield scrapy.Request(
                url=f'{access_trader_direct_API( self.company_id, self.page, 15)}',
                callback=self.parse,
            )
