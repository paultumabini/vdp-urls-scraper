import json
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector

from ..items import ScrapebucketItem
from ..utils import request_all_urls


class CossetteSpider(scrapy.Spider):
    name = 'cossette'
    base_url_api = 'https://oserv3.oreganscdn.com/api/vehicle-inventory-search/?'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
        'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        for url in request_all_urls(self.domain_name, self.base_url_api):
            yield scrapy.Request(
                url=url,
                callback=self.parse,
            )

    def parse(self, response):
        json_res = json.loads(response.body)
        results = json_res.get('search').get('results')
        parsed_html = [Selector(text=html_text.get('html')) for html_text in results]

        for unit in parsed_html:
            url = self.url[:-1]
            sub_url = unit.xpath('//div[@class="ouvsrHeading orH"]/a/@href').get()
            price = unit.xpath('//div [@class="ouvsrCurrentPrice"]/text()')
            p = price.get() if price else 'N/A'

            loader = ItemLoader(item=ScrapebucketItem(), selector=unit)
            loader.add_value('category', f'{url}{sub_url}')
            loader.add_xpath('year', '//span[@class="ouvsrYear"]/text()')
            loader.add_xpath('make', '//span[@class="ouvsrMake"]/text()')
            loader.add_xpath('model', '//span[@class="ouvsrModel"]/text()')
            loader.add_xpath('trim', '//span[@class="ouvsrTrimAndPackage"]/text()')
            loader.add_xpath('stock_number', '//span[@class="ouvsrShortLabel"]/../text()')
            loader.add_xpath('vin', 'substring-after(//ul[@class="ouvsrToolsList otToolbar"]/li[1]/a/@href, "vin=")')
            loader.add_value('vehicle_url', f'{url}{sub_url}')
            loader.add_value('price', p)
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()
