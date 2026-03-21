# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst

from .items_helper import (extract_vin, process_vdp_url, remove_char_from_str,
                           remove_non_numeric, remove_trailing_spaces,
                           set_category)

# from w3lib.html import remove_tags


class ScrapebucketItem(scrapy.Item):
    category = scrapy.Field(input_processor=MapCompose(set_category), output_processor=TakeFirst())
    unit = scrapy.Field(input_processor=MapCompose(remove_trailing_spaces), output_processor=TakeFirst())
    year = scrapy.Field(output_processor=TakeFirst())
    make = scrapy.Field(output_processor=TakeFirst())
    model = scrapy.Field(output_processor=TakeFirst())
    trim = scrapy.Field(output_processor=TakeFirst())
    stock_number = scrapy.Field(input_processor=MapCompose(
        remove_char_from_str, str.strip), output_processor=TakeFirst())
    vin = scrapy.Field(input_processor=MapCompose(extract_vin, str.upper, str.strip), output_processor=TakeFirst())
    vehicle_url = scrapy.Field(input_processor=MapCompose(process_vdp_url), output_processor=TakeFirst())
    msrp = scrapy.Field(input_processor=MapCompose(remove_non_numeric), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(remove_non_numeric), output_processor=TakeFirst())
    selling_price = scrapy.Field(input_processor=MapCompose(remove_non_numeric), output_processor=TakeFirst())
    rebate = scrapy.Field(input_processor=MapCompose(remove_non_numeric), output_processor=TakeFirst())
    discount = scrapy.Field(input_processor=MapCompose(remove_non_numeric), output_processor=TakeFirst())
    image_urls = scrapy.Field(input_processor=MapCompose(remove_char_from_str), output_processor=Join('|'))
    images_count = scrapy.Field(output_processor=TakeFirst())
    image = scrapy.Field(output_processor=TakeFirst())
    page = scrapy.Field(output_processor=TakeFirst())
    domain = scrapy.Field(output_processor=TakeFirst())
