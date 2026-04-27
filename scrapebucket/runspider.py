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
from project.models import Scrape, TargetSite
from scrapebucket.urls_crawl import match_spiders
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import defer, reactor

# Run spiders sequentially
configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)


@defer.inlineCallbacks
def crawl(arg):
    arg_l = arg.lower()

    if arg_l == 'all':
        Scrape.objects.all().delete()
        for spider, url, domain, status in match_spiders(TargetSite, settings):
            if status.lower() != 'active':
                continue
            yield runner.crawl(spider, url=url)
            print(f'Done running: {spider.__name__}')
        reactor.stop()
        return

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


