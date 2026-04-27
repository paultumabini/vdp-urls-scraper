"""Spider for Shopify themes using Re-hash style navigation and Ajaxinate pagination."""

from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem


class RehashSpider(CrawlSpider):
    """
    Crawls listing + paginated pages, then VDPs.

    Vehicle links are discovered from footer anchors (theme-specific) and
    ``ajaxinate`` load-more URLs, not only a single /collections/ path.
    """

    name = 'rehash'
    domain_name = ''

    def start_requests(self):
        # Last two labels of the host (e.g. example.com) for stable domain reporting.
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])

        yield scrapy.Request(url=f'{self.url}collections/all-vehicles')

    # VDP links (theme-dependent XPath).
    link_extractor1 = LinkExtractor(restrict_xpaths='//footer/a')
    # "Next" / ajaxinate pagination chunks.
    link_extractor2 = LinkExtractor(
        restrict_xpaths='//div[@class="ajaxinate-pagination ajax-load "]/a'
    )

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
        # Listing URL lineage (useful if you re-enable per-page or image fields).
        request.meta['page'] = response.url
        return request

    def parse_item(self, response):
        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_xpath('vin', '//ul/li[contains(text(),"VIN: ")]/text()')
        loader.add_value('vehicle_url', response.url)
        loader.add_value('domain', self.domain_name)

        yield loader.load_item()
