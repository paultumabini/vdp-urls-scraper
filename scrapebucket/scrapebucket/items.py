"""
Scrapy item definition for dealer inventory rows.

``input_processor`` runs per value in a list (MapCompose); ``output_processor``
collapses to a single value for the DB (TakeFirst / Join).
"""

import scrapy
from itemloaders.processors import Join, MapCompose, TakeFirst

from .items_helper import (
    extract_vin,
    process_vdp_url,
    remove_char_from_str,
    remove_non_numeric,
    remove_trailing_spaces,
    set_category,
)


class ScrapebucketItem(scrapy.Item):
    # Classification & description
    category = scrapy.Field(
        input_processor=MapCompose(set_category),
        output_processor=TakeFirst(),
    )
    unit = scrapy.Field(
        input_processor=MapCompose(remove_trailing_spaces),
        output_processor=TakeFirst(),
    )
    year = scrapy.Field(output_processor=TakeFirst())
    make = scrapy.Field(output_processor=TakeFirst())
    model = scrapy.Field(output_processor=TakeFirst())
    trim = scrapy.Field(output_processor=TakeFirst())
    stock_number = scrapy.Field(
        input_processor=MapCompose(remove_char_from_str, str.strip),
        output_processor=TakeFirst(),
    )
    vin = scrapy.Field(
        input_processor=MapCompose(extract_vin, str.upper, str.strip),
        output_processor=TakeFirst(),
    )
    vehicle_url = scrapy.Field(
        input_processor=MapCompose(process_vdp_url),
        output_processor=TakeFirst(),
    )
    # Money fields: digits only after helper (see items_helper.remove_non_numeric).
    msrp = scrapy.Field(
        input_processor=MapCompose(remove_non_numeric),
        output_processor=TakeFirst(),
    )
    price = scrapy.Field(
        input_processor=MapCompose(remove_non_numeric),
        output_processor=TakeFirst(),
    )
    selling_price = scrapy.Field(
        input_processor=MapCompose(remove_non_numeric),
        output_processor=TakeFirst(),
    )
    rebate = scrapy.Field(
        input_processor=MapCompose(remove_non_numeric),
        output_processor=TakeFirst(),
    )
    discount = scrapy.Field(
        input_processor=MapCompose(remove_non_numeric),
        output_processor=TakeFirst(),
    )
    image_urls = scrapy.Field(
        input_processor=MapCompose(remove_char_from_str),
        output_processor=Join('|'),
    )
    images_count = scrapy.Field(output_processor=TakeFirst())
    image = scrapy.Field(output_processor=TakeFirst())
    page = scrapy.Field(output_processor=TakeFirst())
    domain = scrapy.Field(output_processor=TakeFirst())
