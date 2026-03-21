import argparse
import os
import sys
from pathlib import Path

# 1. Protect Reactor
from twisted.internet import asyncioreactor
if "twisted.internet.reactor" not in sys.modules:
    asyncioreactor.install()


# 2. Setup environment (Keep this minimal)
sys.path.append(os.path.join(Path(__file__).parents[0], 'scrapebucket'))
sys.path.append(os.path.join(Path(__file__).parents[2], 'webscraping'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')

import django
django.setup()

# 3. Standard Imports
from project.models import TargetSite, Scrape # Import explicitly
from scrapebucket.urls_crawl import match_spiders
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

# import models here as src for pipelines & middleware as well
from project.models import *
from scrapebucket.urls_crawl import match_spiders

# Run spiders sequentially
configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl(arg):
    for results in match_spiders(TargetSite, settings):
        for spider, url, domain, status in results:
            """
            For this setup, delete previous scraped data and save new scraped items.
            """
            if (
                spider.__name__.lower() == f'{arg.lower()}spider'
                and status.lower() == 'active'
            ):
                scrapes_prev = (
                    TargetSite.objects.filter(site_id__exact=domain)
                    .first()
                    .scrapes.all()
                )
                if scrapes_prev.count():
                    scrapes_prev.delete()
                yield runner.crawl(spider, url=url)
                print(f'Done running: {spider.__name__}')
            if arg.lower() == 'all' and status.lower() == 'active':
                scrapes_prev_all = Scrape.objects.all()
                if scrapes_prev_all.count():
                    scrapes_prev_all.delete()
                yield runner.crawl(spider, url=url)
                print(f'Done running: {spider.__name__}')

    reactor.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='spider name')
    parser.add_argument(
        '-s',
        '--spider',
        type=str,
        metavar='',
        required=True,
        help='specify the spider, i.e, the domain name',
    )
    args = parser.parse_args()

    crawl(args.spider)
    #the script will block here until the last crawl call is finished
    reactor.run() 


