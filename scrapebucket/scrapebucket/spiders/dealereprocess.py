from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy_selenium.http import SeleniumRequest

from ..items import ScrapebucketItem


class DealereprocessSpider(scrapy.Spider):
    name = 'dealereprocess'
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.UndetectedChromeDriver': 300},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield SeleniumRequest(
            url=f'{self.url}search/toronto-on/?cy=m4a_1j8',
        )

    def parse(self, response):
        unit_urls = LinkExtractor(restrict_xpaths='//h2[@class="vehicle_title"]/a').extract_links(response)
        for url in unit_urls:
            yield SeleniumRequest(
                url=f'{url.url}',
                callback=self.parse_data,
            )

        next_page_urls = LinkExtractor(restrict_xpaths='//a[@class="thm-inverse_text_color"]').extract_links(response)

        for next_page in next_page_urls:
            yield SeleniumRequest(
                url=f'{next_page.url}',
                callback=self.parse,
            )

    def parse_data(self, response):

        images_urls = response.xpath('//img[contains(@class,"preview_vehicle_image_item")]/@data-src').getall()

        loader = ItemLoader(item=ScrapebucketItem(), selector=response, response=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('stock_number', '//td[contains(text(),"Stock #")]/following-sibling::td/text()')
        loader.add_xpath('vin', '//td[contains(text(),"VIN")]/following-sibling::td/text()')
        loader.add_value('image_urls', images_urls)
        loader.add_value('images_count', len(images_urls))
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
