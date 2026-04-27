import logging
import math
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem
from ..spider_helpers.response_json import loads_response_body
from ..spider_helpers.url_qs import (
    get_company_id,
    keep_top_lvl_domain,
    parse_trader_url,
)

logger = logging.getLogger(__name__)


class TadvantageOrigSpider(scrapy.Spider):
    name = 'tadvantage_orig'
    domain_name = ''
    page = 1

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543
        },
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
    }

    def start_requests(self):
        # kitchener.tabangimotors.com --> kitchenertabangimotors.com
        self.domain_name = keep_top_lvl_domain(urlparse(self.url).netloc).replace(
            'www', ''
        )

        dn = self.domain_name.split('.')[0]

        # get company_id
        self.company_id = get_company_id(dn)
        # if feed_id not found
        if not self.company_id:
            return

        yield scrapy.Request(
            url=f'{parse_trader_url(self.url, self.company_id, self.page, 15)}',
            callback=self.parse,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
            },
            dont_filter=True,
        )

    def parse(self, response):
        json_res = loads_response_body(
            response.body, url=response.url, label=self.name
        )
        if not json_res:
            return

        parsed_data = json_res.get('results') or []
        if not parsed_data:
            logger.warning('tadvantage_orig: empty results for %s', response.url)
            return

        for result in parsed_data:
            loader = ItemLoader(ScrapebucketItem())

            # images = [image.get('image_original') for image in result.get('image', {})]

            vdp_url = result.get('vdp_url')
            if not vdp_url or 'vehicles/' not in vdp_url:
                continue

            indexed = vdp_url.index('vehicles/')
            new_vdp_url = self.url + vdp_url[indexed:]

            loader.add_value('category', result.get('sale_class'))
            loader.add_value('year', result.get('year'))
            loader.add_value('make', result.get('make'))
            loader.add_value('model', result.get('model'))
            loader.add_value('trim', result.get('trim'))
            loader.add_value('stock_number', result.get('stock_number'))
            loader.add_value('vin', result.get('vin'))
            loader.add_value('vehicle_url', new_vdp_url.replace(" ", "%20"))
            loader.add_value('price', result.get('asking_price'))
            # loader.add_value('image_urls', result.get('image').get('image_original'))
            # loader.add_value('images_count', 1)
            loader.add_value('domain', self.domain_name)
            yield loader.load_item()

        summary = json_res.get('summary') or {}
        pages = summary.get('total_vehicles')
        if not pages:
            return

        page_limit = math.ceil(pages / 15)

        if self.page <= page_limit:
            self.page += 1
            yield scrapy.Request(
                url=f'{parse_trader_url(self.url, self.company_id, self.page, 15)}',
                callback=self.parse,
            )
