"""
Map Django ``TargetSite`` rows to Scrapy spider classes for batch runners.

``match_spiders`` yields one record per site row:
``[spider_class, site_url, site_id, status]`` — suitable for ``scrapy crawl``-style drivers
that pass ``-a url=...`` per constructor.
"""

from scrapy import spiderloader


def get_urls(sites, spider_name_class_pairs):
    """
    For each registered spider name, emit all DB rows using that spider.

    ``spider_name_class_pairs``: list of ``[name, spider_class]`` from ``SpiderLoader``.
    """
    for spider_name, spider_class in spider_name_class_pairs:
        qs = sites.objects.filter(spider=spider_name)
        for obj in qs:
            yield [spider_class, obj.site_url, obj.site_id, obj.status]


def match_spiders(target_sites, settings):
    """
    Yield each ``[spider_class, site_url, site_id, status]`` row for all spiders.

    Iterate with ``for spider, url, domain, status in match_spiders(...)``.
    """
    loader = spiderloader.SpiderLoader.from_settings(settings)
    spider_classes = [
        [name, loader.load(name)] for name in loader.list()
    ]
    yield from get_urls(target_sites, spider_classes)
