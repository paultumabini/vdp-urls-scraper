from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from scrapy_selenium import SeleniumRequest

from ..items import ScrapebucketItem
from ..spider_helpers.selenium_helper import SeleniumHelper


class RehashSpider(CrawlSpider):
    name = 'rehash'
    # allowed_domains = []
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        # self.allowed_domains.append(self.domain_name)

        yield scrapy.Request(url=f'{self.url}collections/all-vehicles')
        # yield scrapy.Request(url=f'{self.url}collections/used-cars')

    # vehicle urls
    link_extractor1 = LinkExtractor(restrict_xpaths='//footer/a')
    # pagination urls
    link_extractor2 = LinkExtractor(restrict_xpaths='//div[@class="ajaxinate-pagination ajax-load "]/a')

    rules = (
        Rule(
            link_extractor1,
            callback='parse_item',
            follow=True,
            process_request='meta_processor',
        ),
        Rule(
            link_extractor2,
            follow=True,
            process_request='meta_processor',
        ),
    )

    def meta_processor(self, request, response):
        request.meta['page'] = response.url
        return request

    def parse_item(self, response):
        # page = response.meta['page']
        # image_selector = '//img[contains(@class, "gallery__thumbnail")]/@srcset'
        # wait_until_selector = '//span[contains(@class, "gallery__thumbnail-wrapper")]/img'

        # pages = SeleniumHelper(response.url, image_selector, wait_until_selector).get_page_source()

        # images = [
        #     f"https:{img.partition(' 1x')[0].replace('80x', '1200x')}".replace('\'', '')
        #     for img in Selector(text=pages.page_source).xpath(image_selector).getall()
        # ]
        # images = Selector(text=pages.page_source).xpath(image_selector).getall()

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_xpath('vin', '//ul/li[contains(text(),"VIN: ")]/text()')
        loader.add_value('vehicle_url', response.url)

        # loader.add_xpath('category', '//td[@class="key-name" and contains(text(), "Condition")]/following::td[1]/text()')
        # loader.add_xpath('year', '//td[@class="key-name" and contains(text(), "Year")]/following::td[1]/text()')
        # loader.add_xpath('make', '//td[@class="key-name" and contains(text(), "Make")]/following::td[1]/text()')
        # loader.add_xpath('model', '//td[@class="key-name" and contains(text(), "Model")]/following::td[1]/text()')
        # loader.add_xpath('trim', '//td[@class="key-name" and contains(text(), "Trim")]/following::td[1]/text()')
        # loader.add_xpath('unit', '//h1[@itemprop="name"]/text()')
        # loader.add_xpath('stock_number', '//span[@id="product-sku"]/descendant::span[2]/text()')
        # loader.add_value('image_urls', images)
        # loader.add_value('images_count', len(images))
        # loader.add_value('page', page)
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
