from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import ScrapebucketItem


class WpAstraSpider(CrawlSpider):
    name = 'wp_astra'
    # allowed_domains = ['drivenation.ca']
    domain_name = ''

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
    }

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:])
        yield scrapy.Request(url=f'{self.url}vehicles')

    # vehicle urls
    link_extractor = LinkExtractor(restrict_xpaths='//div/h2/a')

    rules = (
        Rule(
            link_extractor,
            callback='parse_item',
            follow=True,
            process_request=lambda req, res: (req.meta.update({'page': res.url}), req)[1],
        ),
    )

    def parse_item(self, response):
        page = response.meta['page']

        loader = ItemLoader(item=ScrapebucketItem(), selector=response)
        loader.add_value('vehicle_url', response.url)
        loader.add_xpath(
            'stock_number', '//div[contains(text()[normalize-space()],"Stock Number")]/ancestor::node()[3]/following-sibling::div/div/div/div/text()'
        )
        loader.add_xpath('vin', '//div[contains(text()[normalize-space()],"VIN")]/ancestor::node()[3]/following-sibling::div/div/div/div/text()')

        loader.add_value('domain', self.domain_name)
        yield loader.load_item()
