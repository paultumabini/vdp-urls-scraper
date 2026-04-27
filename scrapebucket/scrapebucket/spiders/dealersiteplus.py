"""Carpages / Dealersite+ style WordPress inventory (mixed microdata and table VIN rows)."""

from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings

from ..items import ScrapebucketItem


class DealersiteplusSpider(CrawlSpider):
    """
    Entry paths differ by site install (``all-vehicles``, ``new-inventory``, ``vehicles``).

    Pagination uses WordPress ``page-numbers``; some themes need an explicit User-Agent on
    follow-up requests (``set_user_agent``).
    """

    name = 'dealersiteplus'  # carpages
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        for page in ['all-vehicles/', 'new-inventory/', 'vehicles/']:
            yield scrapy.Request(url=f'{self.url}{page}')

    link_extractor1 = LinkExtractor(
        restrict_xpaths=[
            '//h4/a[contains(@title,*)]',
            '//div[@class="featured-card"]/a',
        ]
    )
    link_extractor2 = LinkExtractor(
        restrict_xpaths='//a[@class="next page-numbers"]'
    )

    rules = (
        Rule(
            link_extractor1,
            callback='parse_item',
            follow=True,
        ),
        Rule(
            link_extractor2,
            follow=True,
            process_request='set_user_agent',
        ),
    )

    def set_user_agent(self, request, spiders):
        request.headers['User-Agent'] = get_project_settings().get('USER_AGENT')
        return request

    def parse_item(self, response):
        # Microdata-first; table/div fallbacks for themes without schema.org productID.
        vin1 = response.xpath('//li[@itemprop="productID"]/span/text()').get()
        vin2 = response.xpath('(//td[contains(text(),"VIN:")]/../td)[2]//text()').get()
        vin3 = response.xpath('//div[contains(text(),"VIN:")]/text()').get()
        vin4 = response.xpath('(//div[contains(text(),"VIN:")]/../div)[2]//text()').get()

        vin = vin1 or vin2 or vin3

        # Known layout conflict: this domain exposes VIN in the fourth xpath variant only.
        if self.domain_name == 'spadonileasing.com':
            vin = vin4

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath('year', '//span[@itemprop="releaseDate"]/text()')
        loader.add_xpath('make', '//span[@itemprop="brand"]/text()')
        loader.add_xpath('model', '//span[@itemprop="model"]/text()')
        loader.add_value('vin', vin)
        loader.add_xpath('stock_number', '//li[@itemprop="sku"]/text()')
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
