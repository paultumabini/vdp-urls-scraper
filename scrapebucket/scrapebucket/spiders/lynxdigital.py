from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings

from ..items import ScrapebucketItem


class LynxdigitalSpider(CrawlSpider):
    name = 'lynxdigital'
    # allowed_domains = []
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield scrapy.Request(url=f'{self.url}vehicles/')

    # vehicle urls
    extractor1 = LinkExtractor(restrict_xpaths='//h3[starts-with(@class,"product-title")]/a')
    # pagination urls
    extractor2 = LinkExtractor(restrict_xpaths='//nav[@class="woocommerce-pagination"]/descendant::a[@class="next page-numbers"]')

    rules = (
        Rule(extractor1, callback='parse_item', follow=True),
        Rule(extractor2, follow=True, process_request='set_user_agent'),
    )

    def set_user_agent(self, request, spiders):
        request.headers['User-Agent'] = get_project_settings().get('USER_AGENT')
        return request

    def parse_item(self, response):
        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_xpath(
            'vin', '//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_vin"]/td/p/a/text()'
        )
        loader.add_value('vehicle_url', response.url)
        # loader.add_value('category', response.url)
        # loader.add_xpath('unit', '//h1[@itemprop ="name"]/text()')
        # loader.add_xpath(
        #     'stock_number',
        #     '//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_stock-number"]/td/p/a/text()',
        # )
        # loader.add_xpath('price', '//span[@class="woocommerce-Price-currencySymbol"]/../text()')
        # loader.add_xpath('image_urls', '//div[@data-thumb]/@data-thumb')
        # loader.add_value('images_count', len(response.xpath('//div[@data-thumb]/@data-thumb').getall()))

        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
