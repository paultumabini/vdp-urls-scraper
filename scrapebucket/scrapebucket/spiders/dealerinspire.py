from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy_selenium.http import SeleniumRequest

from ..items import ScrapebucketItem


class DealerinspireSpider(scrapy.Spider):
    name = 'dealerinspire'
    # allowed_domains = []
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.UndetectedChromeDriver': 300},
        'SPIDER_MIDDLEWARES': {'scrapebucket.middlewares.JobStatLogsMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield SeleniumRequest(
            url=f'{self.url}dealer-inspire-inventory/inventory_sitemap/',
        )

    def parse(self, response):
        unit_urls = LinkExtractor(restrict_xpaths='//td/a').extract_links(response)
        for url in unit_urls:
            yield SeleniumRequest(
                url=f'{url.url}',
                callback=self.parse_data,
            )

    def parse_data(self, response):

        category = 'used' if 'used' in response.url else 'new'
        images = [
            response.xpath(
                '//div[@class="swiper-container vdp-gallery-modal__main swiper-container-horizontal"]/div[@class="swiper-wrapper"]/div[contains(@class,"swiper-slide")]/img/@src'
            ).getall(),
            response.xpath(
                '//div[@class="swiper-container vdp-gallery-modal__main swiper-container-horizontal"]/div[@class="swiper-wrapper"]/div[contains(@class,"swiper-slide")]/img/@data-src'
            ).getall(),
        ]

        as_unit = response.xpath('//div[@class="vdp-title__vehicle-info"]/h1/text()').get()
        price = (
            response.xpath('//span[@class="price"]/text()').get()
            if response.xpath('//span[@class="price"]/text()').get()
            else response.xpath('//span[@class="pricing-item__price "]/text()').get()
        )

        stock_number1 = response.xpath('//ul[@class="vdp-title__vin-stock"]/li[2]/span/../text()[2]').get()
        vin1 = response.xpath('//ul[@class="vdp-title__vin-stock"]/li[1]/..//span[@id="vin"]/text()').get()

        stock_number2 = response.xpath('(//span[@class="vinstock-number"]/text())[1]').get()
        vin2 = response.xpath('(//span[@class="vinstock-number"]/text())[2]').get()

        stock_number = stock_number1 if stock_number1 else stock_number2
        vin = vin1 if vin1 else vin2

        loader = ItemLoader(item=ScrapebucketItem(), selector=response, response=response)
        loader.add_value('stock_number', stock_number)
        loader.add_value('vin', vin)
        loader.add_value('vehicle_url', response.url)
        loader.add_value('domain', self.domain_name)
        loader.add_value('category', category)
        loader.add_value('unit', as_unit)
        loader.add_value('price', price)
        loader.add_value('image_urls', '|'.join([*images[0], *images[1]]))
        loader.add_value('images_count', len([*images[0], *images[1]]))

        yield loader.load_item()
