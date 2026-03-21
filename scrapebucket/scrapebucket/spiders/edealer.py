import json
from urllib.parse import urlparse

import requests
import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector

from ..items import ScrapebucketItem


class EdealerSpider(scrapy.Spider):
    name = 'edealer'
    domain_name = ''

    def start_requests(self):
        self.domain_name = '.'.join(urlparse(self.url).netloc.split('.')[-2:]).replace('-', '')

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": f"{self.url}",
            "Referer": f"{self.url}new/",
            "Sec-Ch-ua": """Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111""",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        yield scrapy.FormRequest(
            url=f'{self.url}new/',
            method='POST',
            headers=headers,
            formdata={
                "ajax": "true",
                "refresh": "true",
            },
        )

        yield scrapy.FormRequest(
            url=f'{self.url}used/',
            method='POST',
            headers=headers,
            formdata={
                "ajax": "true",
                "refresh": "true",
            },
        )

    def parse(self, response):
        res = json.loads(response.body)
        items = res.get('vehicles')

        for item in items:
            html = Selector(text=item.get('vehicleCellHTML'))

            vin1 = html.xpath('//input/@value').get()
            vin2 = html.xpath('//div[@class="vehicle-information-grid"]/following-sibling::input/@value').get()

            vdp_url1 = html.xpath('//div[contains(@class,"vehicle-list-cell")]/@itemid').get()
            vdp_url2 = html.xpath('//p[@class="vehicle-year-make-model"]/a/@href').get()

            vin = vin1 if vin1 else vin2
            vdp_url = vdp_url1 if vdp_url1 else vdp_url2

            loader = ItemLoader(ScrapebucketItem())
            loader.add_value('vehicle_url', f'{self.url}{vdp_url[1:]}')
            loader.add_value('vin', vin)
            loader.add_value('domain', self.domain_name)

            yield loader.load_item()

        has_next_page = res.get('nextURL')

        if has_next_page:
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": f"{self.url}",
                "Referer": f"{self.url}{has_next_page}",
                "Sec-Ch-ua": """Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111""",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }
            yield scrapy.FormRequest(
                url=f'{self.url}{has_next_page}',
                method='POST',
                headers=headers,
                formdata={
                    'ajax': 'true',
                    'refresh': 'true',
                },
                callback=self.parse,
            )
