"""Typesense ``multi_search`` spider (hosted collection + API key on the query string)."""

import json
import logging

import scrapy

from ..spider_helpers.response_json import loads_response_body

logger = logging.getLogger(__name__)


class ZopDealerSpider(scrapy.Spider):
    """
    Single POST template walks the SRP; ``out_of`` from the first batch mutates ``per_page``.

    NOTE: This mirrors a legacy integration (key in URL). Prefer env-driven endpoints/keys
    if you externalize configuration.
    """

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
                "page": "1",
                "per_page": "24",
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
        res_dict = loads_response_body(
            response.body, url=response.url, label=self.name
        )
        if not res_dict:
            return

        results = res_dict.get('results') or []
        if not results:
            logger.warning('zopdealer: no results in response')
            return

        batch = results[0]
        out_of = batch.get('out_of')
        if out_of is not None:
            self.per_page = out_of
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

        units = batch.get('hits') or []
        for i, unit in enumerate(units):
            doc = unit.get('document') or {}
            logger.debug(
                'zopdealer item %s stock=%s vin=%s',
                i + 1,
                doc.get('stock_no'),
                doc.get('vin'),
            )
