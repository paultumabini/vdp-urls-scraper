"""
Entry point for running Scrapy spiders against the AIM dealer database.

Usage::

    python runspider.py --spider <domain>   # run one spider  (e.g. ``autojini``)
    python runspider.py --spider all        # run every active spider sequentially

Bootstrap order (order matters):
  1. Install the asyncio Twisted reactor — must happen before any other Twisted import.
  2. Bootstrap Django ORM via ``ensure_django()`` so models are available at import time
     in middlewares and pipelines.
  3. Import Scrapy/project modules that depend on the above.
"""

import argparse
import sys

# ---------------------------------------------------------------------------
# 1. Reactor — install before *any* ``twisted.internet`` import elsewhere.
#    Playwright and other async spiders require the asyncio-backed reactor.
# ---------------------------------------------------------------------------
from twisted.internet import asyncioreactor

if 'twisted.internet.reactor' not in sys.modules:
    asyncioreactor.install()

# ---------------------------------------------------------------------------
# 2. Django ORM bootstrap (idempotent; no-op if already called by settings.py).
#    Locates manage.py, patches sys.path, sets DJANGO_SETTINGS_MODULE, and
#    calls django.setup().
# ---------------------------------------------------------------------------
from scrapebucket.django_setup import ensure_django

ensure_django()

# ---------------------------------------------------------------------------
# 3. Application imports — safe now that Twisted reactor and Django are ready.
# ---------------------------------------------------------------------------
from project.models import Scrape, TargetSite
from scrapebucket.urls_crawl import match_spiders
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl(arg: str):
    """Schedule spiders sequentially via ``CrawlerRunner``, then stop the reactor."""
    arg_l = arg.lower()

    if arg_l == 'all':
        # Full re-crawl: wipe all previous scrape records first.
        Scrape.objects.all().delete()
        for spider, url, domain, status in match_spiders(TargetSite, settings):
            if status.lower() != 'active':
                continue
            yield runner.crawl(spider, url=url)
            print(f'Done running: {spider.__name__}')
        reactor.stop()
        return

    # Single-spider mode: match by name, delete only that site's prior scrapes.
    for spider, url, domain, status in match_spiders(TargetSite, settings):
        if status.lower() != 'active':
            continue
        if spider.__name__.lower() != f'{arg_l}spider':
            continue
        ts = TargetSite.objects.filter(site_id__exact=domain).first()
        if ts is not None:
            ts.scrapes.all().delete()
        yield runner.crawl(spider, url=url)
        print(f'Done running: {spider.__name__}')

    reactor.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run one or all active Scrapy spiders.')
    parser.add_argument(
        '-s',
        '--spider',
        type=str,
        metavar='NAME',
        required=True,
        help='Spider domain name (e.g. "autojini") or "all" to run every active spider.',
    )
    args = parser.parse_args()

    crawl(args.spider)
    # Blocks until the last crawl call completes and reactor.stop() is reached.
    reactor.run()
