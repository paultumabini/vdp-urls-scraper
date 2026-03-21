import json
from urllib.parse import urlparse

import scrapy
from scrapy.loader import ItemLoader

from ..items import ScrapebucketItem
from ..utils import COOKIE_NOVLANBROS, cookie_parser


class ZopDealerSpider(scrapy.Spider):
    name = 'zopdealer'
    page = 1
    per_page = 24

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
        'SPIDER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketSpiderMiddleware': 543},
    }

    query = {
        "searches": [
            {
                "query_by": "make,model,year_search,trim,vin,stock_no,exterior_color",
                "num_typos": 0,
                "sort_by": "status_rank:asc,created_at:desc",
                "highlight_full_fields": "make,model,year_search,trim,vin,stock_no,exterior_color",
                "collection": "fa3feaedad1ba3fc26135c6f8b28d80d",
                "q": "*",
                "facet_by": "make,model,selling_price,year",
                "filter_by": "",
                "max_facet_values": 50,
                "page": f"{page}",
                "per_page": f"{per_page}",
            }
        ]
    }

    def start_requests(self):
        self.url = 'https://v6eba1srpfohj89dp-1.a1.typesense.net/multi_search?x-typesense-api-key=cWxPZGNaVWpsUTlzN2szWmExNTJxZWNiWUM5MnRqa2xkRjdZcWZuclZMbz1oZmUweyJmaWx0ZXJfYnkiOiJzdGF0dXM6W0luc3RvY2ssIFNvbGRdICYmIHZpc2liaWxpdHk6PjAgJiYgcHJpY2U6PjAgJiYgZGVsZXRlZF9hdDo9MCJ9'

        yield scrapy.Request(
            url=f'{self.url}',
            method='POST',
            headers={
                'Content-Type': 'application/json',
            },
            body=json.dumps(self.query),
            callback=self.parse,
        )

    def parse(self, response):
        res_dict = json.loads(response.body)

        self.per_page = res_dict.get('results')[0].get('out_of')
        self.query.get('searches')[0].update({'per_page': self.per_page})

        yield scrapy.Request(
            url=f'{self.url}',
            method='POST',
            headers={
                'Content-Type': 'application/json',
            },
            body=json.dumps(self.query),
            callback=self.parse,
        )

        units = res_dict.get('results')[0].get('hits')

        for i, unit in enumerate(units):
            print(i + 1, unit.get('document').get('stock_no'), unit.get('document').get('vin'))
