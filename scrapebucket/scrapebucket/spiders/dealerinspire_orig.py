from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium.http import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import ScrapebucketItem
from ..spider_helpers.selenium_helper import SeleniumHelper


class DealerinspireSpider(scrapy.Spider):
    name = 'dealerinspire_orig'
    # allowed_domains = ['taylorcadillac.ca', 'rosetownmainline.net']
    domain_name = ''

    custom_settings = {
        # 'ITEM_PIPELINES': {'scrapebucket.pipelines.DealerinspirePipeline': 300},
        'DOWNLOAD_DELAY': 10,
    }

    def start_requests(self):
        # extract domain name
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        base_url = f'{self.url}new-vehicles/?_paymentType=our_price'
        pagination_selector = '//div[@class="pagination-state"]/text()'
        wait_until_selector = '//div[@class="pagination-state"]'

        pages = SeleniumHelper(base_url, pagination_selector, wait_until_selector).get_pagination_remove_text()

        for page in range(pages + 1):
            yield SeleniumRequest(
                url=f'{self.url}new-vehicles/?p={page}&_paymentType=our_price',
                wait_time=10,
                # wait_until=EC.presence_of_all_elements_located((By.XPATH, '//div[@class="pagination-arrow pagination-next"]/a')),
            )

    def parse(self, response):
        for unit in response.xpath('//div[@class="hit"]'):
            yield SeleniumRequest(
                url=unit.xpath('.//a/@href').get(),
                callback=self.parse_data,
                meta={'unit': unit, 'page': response.url},
            )

    def parse_data(self, response):
        unit = response.request.meta['unit']
        page = response.request.meta['page']
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
        stock_number = response.xpath('//ul[@class="vdp-title__vin-stock"]/li[2]/span/../text()[2]').get()
        price = (
            response.xpath('//span[@class="price"]/text()').get()
            if response.xpath('//span[@class="price"]/text()').get()
            else response.xpath('//span[@class="pricing-item__price "]/text()').get()
        )

        loader = ItemLoader(item=ScrapebucketItem(), selector=unit, response=response)
        loader.add_value('category', category)
        loader.add_value('unit', as_unit)
        loader.add_value('price', price)
        loader.add_value('stock_number', stock_number)
        loader.add_xpath('vin', './/a/@href')
        loader.add_xpath('vehicle_url', './/a/@href')
        loader.add_value('image_urls', '|'.join([*images[0], *images[1]]))
        loader.add_value('images_count', len([*images[0], *images[1]]))
        loader.add_value('page', page)
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
