from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy_selenium.http import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ..items import ScrapebucketItem
from ..spider_helpers.selenium_helper import SeleniumHelper


class WpAvadaSpider(scrapy.Spider):
    name = 'wp_avada'
    domain_name = ''

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        pagination_selector = '//a[@class="inactive"]/text()'
        wait_until_selector = '//a[@class="inactive"]'
        pages = SeleniumHelper(f'{self.url}inventory/', pagination_selector, wait_until_selector).get_pagination_remove_text()

        for page in range(pages + 1):
            yield SeleniumRequest(
                url=f'{self.url}inventory/page/{page}',
                wait_time=10,
                wait_until=EC.element_to_be_clickable((By.XPATH, wait_until_selector)),
                callback=self.parse,
            )

    def parse(self, response):
        unit_urls = LinkExtractor(restrict_xpaths='//h1[@class="title-heading-left"]/a').extract_links(response)
        for url in unit_urls:
            yield scrapy.Request(
                url=f'{url.url}',
                callback=self.parse_data,
                meta={'page': response.url},
            )

    def parse_data(self, response):
        page = response.request.meta['page']

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('stock_number', '//li[contains(text(),"Stock #: ")]/span/text()')
        loader.add_xpath('vin', '//li[contains(text(),"VIN: ")]/span/text()')
        loader.add_xpath('price', '(//span[@class="woocommerce-Price-currencySymbol"])[1]/../text()')
        loader.add_xpath('image_urls', '//a[@class="avada-product-gallery-lightbox-trigger"]/@href')
        loader.add_value('images_count', len(response.xpath('//a[@class="avada-product-gallery-lightbox-trigger"]/@href').getall()))
        loader.add_value('page', page)
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
