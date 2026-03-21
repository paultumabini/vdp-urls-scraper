from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem
from ..spider_helpers.playwright_helper import PlaywrightHelper


class D2cmediaSpider(CrawlSpider):
    name = 'd2cmedia'
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        # get page number thru playwright helper class
        pagination_selector = '//span[@class="s-name"]'
        wait_until_selector = '//span[@class="s-name"]'
        # pages = PlaywrightHelper(
        #     f'{self.url}inventory.html?filterid=a1b13q0-10x0-0-0',
        #     pagination_selector,
        #     wait_until_selector,
        # ).get_page_num_src('get_pagination_no_text')

        for page in range(8 + 1):
            yield scrapy.Request(
                url=f'{self.url}inventory.html?filterid=a1b123d19q{page}-10x0-0-0',
                meta={'page': page},
            )

            yield scrapy.Request(
                url=f'{self.url}inventory.html?filterid=a1b13q{page}-10x0-0-0',
                meta={'page': page},
            )

            yield scrapy.Request(
                url=f'{self.url}inventory.html?filterid=a1b2q{page}-10x0-0-0',
                meta={'page': page},
            )

    rules = (
        Rule(
            LinkExtractor(restrict_xpaths='//div[contains(@class,"carImage")]/a'),
            callback='parse_item',
            follow=True,
            process_request=lambda req, res: (req.meta.update({'page': res.meta['page']}), req)[1],
        ),
    )

    def parse_item(self, response):
        page = response.meta['page']
        vin1 = response.xpath('//span[@id="specsVin"]/text()').get()
        vin2 = response.xpath('//input[@id="expresscarvin"]/@value').get()
        vin3 = response.xpath('//input[@id="carproofcarvin"]/@value').get()
        vin = vin1 if vin1 else vin2 if vin2 else vin3

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vin', vin)
        loader.add_value('vehicle_url', response.url)
        # loader.add_value('category', response.url)
        # loader.add_xpath('year', '//input[@name="year"]/@value')
        # loader.add_xpath('make', '//input[@name="make"]/@value')
        # loader.add_xpath('model', '//input[@name="model"]/@value')
        # loader.add_xpath('trim', '//input[@name="trim"]/@value')
        # loader.add_xpath('unit', 'normalize-space(translate(//div[@class="makeModelYear"]/text(),"\u00A0",""))')
        # loader.add_xpath('stock_number', '//span[@id="specsNoStock"]/text()')
        # loader.add_xpath('price', '//input[@name="vehiclePrice"]/@value')
        # loader.add_xpath('image_urls', '//li[@class="slide"]/a/@href')
        # loader.add_value('images_count', len(response.xpath('//li[@class="slide"]/a/@href').getall()))
        # loader.add_value('page', f'page {page}')
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
