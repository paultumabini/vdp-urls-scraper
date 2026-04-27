"""D2C Media inventory: multiple legacy ``filterid`` query shapes on the same dealer."""

from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem


class D2cmediaSpider(CrawlSpider):
    """
    Hits several ``inventory.html?filterid=...`` patterns per page index.

    Older deployments used Playwright to read total pages from the DOM; the
    current approach uses a fixed page cap (0..8) and three filter variants
    per index to cover template differences without one-off discovery.
    """

    name = 'd2cmedia'
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        # One-based page indices in the query string; cap limits crawl depth if pagination is unknown.
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
            process_request='carry_page_meta',
        ),
    )

    def carry_page_meta(self, request, response):
        # List responses set ``page`` in ``start_requests``; keep it when following to VDPs.
        request.meta['page'] = response.meta.get('page', response.url)
        return request

    def parse_item(self, response):
        # VIN is exposed in different inputs depending on VDP layout / integrations.
        vin1 = response.xpath('//span[@id="specsVin"]/text()').get()
        vin2 = response.xpath('//input[@id="expresscarvin"]/@value').get()
        vin3 = response.xpath('//input[@id="carproofcarvin"]/@value').get()
        vin = vin1 or vin2 or vin3

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vin', vin)
        loader.add_value('vehicle_url', response.url)
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
