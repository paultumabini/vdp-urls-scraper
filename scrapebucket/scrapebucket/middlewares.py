"""
Scrapy downloader/spider middlewares and Selenium integration.

Side effect on import: configures ``sys.path``, ``DJANGO_SETTINGS_MODULE``, and calls
``django.setup()`` so ORM models (``runspider``) resolve. Spiders using Playwright/async
rely on ``DJANGO_ALLOW_ASYNC_UNSAFE`` (documented Django limitation for mixed sync ORM).
"""

from __future__ import annotations

import csv
import io
import logging
import os
import sys
from ftplib import FTP, error_perm
from importlib import import_module
from pathlib import Path

import django
import pytz
from scrapy import signals

logger = logging.getLogger(__name__)

# Project root = parent of ``scrapebucket/`` package (directory that contains ``manage.py``).
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_root = str(_PROJECT_ROOT)
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')
# Allows synchronous ORM access from spider_closed and similar hooks when Twisted/async
# handlers are present elsewhere in the stack (use sync_to_async in new code if possible).
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
django.setup()

from project.models import SpiderLog, TargetSite

import undetected_chromedriver as uc
from scrapy_selenium.middlewares import SeleniumMiddleware
from selenium_stealth import stealth


class ScrapebucketSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapebucketDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumStealthMiddleware(SeleniumMiddleware):
    """scrapy-selenium driver with selenium-stealth applied (legacy Chrome options)."""

    def __init__(
        self,
        driver_name,
        driver_executable_path,
        driver_arguments,
        browser_executable_path,
    ):
        webdriver_base_path = f'selenium.webdriver.{driver_name}'

        driver_klass_module = import_module(f'{webdriver_base_path}.webdriver')
        driver_klass = getattr(driver_klass_module, 'WebDriver')

        driver_options_module = import_module(f'{webdriver_base_path}.options')
        driver_options_klass = getattr(driver_options_module, 'Options')

        driver_options = driver_options_klass()

        if browser_executable_path:
            driver_options.binary_location = browser_executable_path
        for argument in driver_arguments:
            driver_options.add_argument(argument)

        driver_kwargs = {
            'executable_path': driver_executable_path,
            f'{driver_name}_options': driver_options,
        }

        driver_options.add_argument('--headless')
        driver_options.add_argument('--disable-blink-features=AutomationControlled')
        driver_options.add_argument('--disable-dev-shm-usage')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--disable-gpu')
        driver_options.add_argument('--incognito')

        self.driver = driver_klass(**driver_kwargs)

        stealth(
            self.driver,
            languages=['en-US', 'en'],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer='Intel Iris OpenGL Engine',
            fix_hairline=True,
        )


class UndetectedChromeDriver(SeleniumMiddleware):
    """Headless undetected-chromedriver (minimal options; expand per deployment)."""

    def __init__(
        self,
        driver_name,
        driver_executable_path,
        driver_arguments,
        browser_executable_path,
    ):
        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument('--headless')
        self.driver = uc.Chrome(options=options)


class JobStatLogsMiddleware:
    """On spider close, persist crawl stats to ``SpiderLog`` for the target site."""

    def __init__(self, crawler):
        self.stats = crawler.stats

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_closed(self, spider, reason):
        stats = spider.crawler.stats.get_stats()
        bot_name = spider.crawler.settings.get('BOT_NAME')

        domain_name = spider.domain_name.split('.')[0]

        target = TargetSite.objects.filter(site_id__exact=domain_name).first()
        if target is None:
            logger.warning(
                'JobStatLogsMiddleware: no TargetSite for site_id=%r; skip SpiderLog',
                domain_name,
            )
            return

        try:
            job_logs = {
                'target_site_id': target.pk,
                'spider_name': spider.name,
                'allowed_domain': domain_name,
                'items_scraped': stats.get('item_scraped_count'),
                'items_dropped': stats.get('item_dropped_count'),
                'finish_reason': stats.get('finish_reason'),
                'request_count': stats.get('downloader/request_count'),
                'status_count_200': stats.get('downloader/response_status_count/200'),
                'start_timestamp': stats.get('start_time'),
                'end_timestamp': stats.get('finish_time'),
                'elapsed_time': self.dt_interval(stats.get('elapsed_time_seconds')),
                'elapsed_time_seconds': stats.get('elapsed_time_seconds'),
            }
            SpiderLog(**job_logs).save()
            logger.info(
                'Crawl finished: bot=%s spider=%s target=%s',
                bot_name,
                spider.name,
                domain_name,
            )
        except Exception as exc:
            logger.exception('JobStatLogsMiddleware: failed to save SpiderLog: %s', exc)

    def convert_dt(self, dt):
        return (
            pytz.utc.localize(dt)
            .astimezone(pytz.timezone('US/Eastern'))
            .strftime('%Y-%m-%d %I:%M:%S')
        )

    def dt_interval(self, s):
        if s is None:
            return '00:00:00'
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


class VdpUrlsMiddleWare:
    """After crawl: export VIN/VDP rows for this site to FTP as ``VDP_URLS_{site_id}.csv``."""

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_closed(self, spider, reason):
        domain_name = spider.domain_name.split('.')[0]
        self.send_to_ftp(domain_name, spider)

    def send_to_ftp(self, pk, spider):
        target = TargetSite.objects.filter(site_id=pk).first()
        if target is None:
            logger.warning(
                'VdpUrlsMiddleWare: no TargetSite for site_id=%r; skip FTP export',
                pk,
            )
            return

        host = os.environ.get('AIM_FTP_HOST')
        user = os.environ.get('AIM_FTP_USER')
        password = os.environ.get('AIM_FTP_PASS')
        if not all((host, user, password)):
            logger.warning(
                'VdpUrlsMiddleWare: AIM_FTP_* env vars not set; skip FTP export',
            )
            return

        csvfile = io.StringIO()
        fieldnames = ['VIN', 'VDP URLS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in target.scrapes.values():
            writer.writerow(
                {
                    'VIN': item.get('vin'),
                    'VDP URLS': item.get('vehicle_url'),
                }
            )

        payload = io.BytesIO(csvfile.getvalue().encode('utf-8'))
        remote = f'VDP_URLS_{pk}.csv'

        ftp = FTP()
        try:
            ftp.connect(host, int(os.environ.get('AIM_FTP_PORT', '21')))
            ftp.login(user, password)
            ftp.storbinary(f'STOR {remote}', payload)
            logger.info('VdpUrlsMiddleWare: uploaded %s', remote)
        except (OSError, error_perm) as exc:
            logger.error('VdpUrlsMiddleWare: FTP upload failed: %s', exc)
        finally:
            try:
                ftp.quit()
            except Exception:
                ftp.close()
