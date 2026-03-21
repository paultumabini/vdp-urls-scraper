import json
from urllib.parse import urlparse

import scrapy
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy_selenium.http import SeleniumRequest

from ..items import ScrapebucketItem


class FlexdealerSpider(scrapy.Spider):
    name = 'flexdealer'

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        for inventory in ['new-hyundai-inventory', 'used-inventory']:
            yield SeleniumRequest(
                url=f'{self.url}{inventory}',
                callback=self.parse,
            )

    def parse(self, response):
        res = Selector(text=response.text)
        # select elements at <script> tags
        json_txt = res.xpath('//script[contains(.,"var vehicles")]/text()').get().replace("var vehicles = ", "").replace(";", "")
        json_dict = json.loads(json_txt)

        for dic in json_dict:
            url = dic.get('url')
            vin = dic.get('vin')
            stock = dic.get('stock')

            yield SeleniumRequest(
                url=f'{self.url[:-1]}{url}',
                callback=self.parse_data,
                meta={'vin': vin, 'stock': stock},
            )

    def parse_data(self, response):
        vin = response.request.meta['vin']
        stock = response.request.meta['stock']

        images_txt = response.xpath('//a[@data-stateventlabel="VDP Photos Image"]/@data-cargo').get()
        img_urls = Selector(text=images_txt).xpath('//@src').getall()
        images = [f'{self.url[:-1]}{img}' for img in img_urls]

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_value('vin', vin)
        # loader.add_value('stock_number', stock)
        # loader.add_value('image_urls', images)
        # loader.add_value('images_count', len(images))
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
