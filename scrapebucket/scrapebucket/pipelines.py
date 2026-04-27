"""
Persist scraped items to Django ``Scrape`` rows keyed by ``TargetSite.site_id``.

Import-time bootstrap matches ``middlewares`` (path + ``django.setup()``) so ORM is ready
when the pipeline runs.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import django
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_root = str(_PROJECT_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from project.models import Scrape, TargetSite


class ScrapebucketPipeline:
    """Default pipeline: map item domain → ``TargetSite``, insert ``Scrape``."""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        domain = adapter.get('domain')
        if not domain:
            logger.debug('ScrapebucketPipeline: item without domain; skip DB write')
            return item

        domain_name = domain.split('.')[0]
        target = TargetSite.objects.filter(site_id__iexact=domain_name).first()
        if target is None:
            logger.warning(
                'ScrapebucketPipeline: no TargetSite for site_id=%r; skip',
                domain_name,
            )
            return item

        try:
            scrape_data = {
                'target_site_id': target.pk,
                'spider': spider.name,
                'category': adapter.get('category'),
                'unit': adapter.get('unit'),
                'year': adapter.get('year'),
                'make': adapter.get('make'),
                'model': adapter.get('model'),
                'trim': adapter.get('trim'),
                'stock_number': adapter.get('stock_number'),
                'vin': adapter.get('vin'),
                'vehicle_url': adapter.get('vehicle_url'),
                'msrp': adapter.get('msrp'),
                'price': adapter.get('price'),
                'selling_price': adapter.get('selling_price'),
                'rebate': adapter.get('rebate'),
                'image_urls': adapter.get('image_urls'),
                'images_count': adapter.get('images_count'),
                'page': adapter.get('page'),
            }
            Scrape(**scrape_data).save()
        except Exception as exc:
            logger.exception('ScrapebucketPipeline: save failed: %s', exc)

        return item


class DealerinspireXmlPipeline:
    """Placeholder / debug pipeline for Dealer Inspire XML experiments."""

    def process_item(self, item, spider):
        logger.debug('DealerinspireXmlPipeline item=%s', item)
        return item
