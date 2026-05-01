"""
Persist scraped items to Django ``Scrape`` rows keyed by ``TargetSite.site_id``.

Django ORM is bootstrapped via ``ensure_django()`` (idempotent; a no-op when
``settings.py`` has already called it).
"""

from __future__ import annotations

import logging

from itemadapter import ItemAdapter

from scrapebucket.django_setup import ensure_django

# Safety net: no-op when settings.py has already bootstrapped Django; ensures
# the ORM is available if this module is ever imported in isolation.
ensure_django()

logger = logging.getLogger(__name__)

from project.models import Scrape, TargetSite  # noqa: E402 — must follow ensure_django()


class ScrapebucketPipeline:
    """
    Default pipeline: resolve item domain → ``TargetSite``, then insert a ``Scrape``.

    ``domain`` is expected to be the full registered domain (e.g. ``"example.com"``).
    The leading label (``"example"``) is matched case-insensitively against
    ``TargetSite.site_id``.  Items without a domain or with no matching site are
    skipped without raising.
    """

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        domain = adapter.get('domain')
        if not domain:
            logger.debug('ScrapebucketPipeline: item has no domain field; skip DB write')
            return item

        # Strip TLD/subdomains — site_id stores only the registrable label (e.g. "example").
        domain_name = domain.split('.')[0]
        target = TargetSite.objects.filter(site_id__iexact=domain_name).first()
        if target is None:
            logger.warning(
                'ScrapebucketPipeline: no TargetSite for site_id=%r; skip',
                domain_name,
            )
            return item

        try:
            Scrape(
                target_site_id=target.pk,
                spider=spider.name,
                category=adapter.get('category'),
                unit=adapter.get('unit'),
                year=adapter.get('year'),
                make=adapter.get('make'),
                model=adapter.get('model'),
                trim=adapter.get('trim'),
                stock_number=adapter.get('stock_number'),
                vin=adapter.get('vin'),
                vehicle_url=adapter.get('vehicle_url'),
                msrp=adapter.get('msrp'),
                price=adapter.get('price'),
                selling_price=adapter.get('selling_price'),
                rebate=adapter.get('rebate'),
                image_urls=adapter.get('image_urls'),
                images_count=adapter.get('images_count'),
                page=adapter.get('page'),
            ).save()
        except Exception as exc:
            logger.exception('ScrapebucketPipeline: save failed: %s', exc)

        return item


class DealerinspireXmlPipeline:
    """
    Debug/experimental pipeline for Dealer Inspire XML spiders.

    Logs each item at DEBUG level; does not write to the database.
    Enable in settings via ``ITEM_PIPELINES`` when troubleshooting XML output.
    """

    def process_item(self, item, spider):
        logger.debug('DealerinspireXmlPipeline item=%s', item)
        return item
