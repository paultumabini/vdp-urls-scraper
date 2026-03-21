# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import csv
import io
import logging
import os
import sys
from ftplib import FTP
from functools import reduce
from pathlib import Path

import django
import pytz

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter, is_item
from scrapy import signals

sys.path.append(os.path.join(Path(__file__).parents[3], 'webscraping'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webscraping.settings'
# Django: SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async
# use: os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from runspider import SpiderLog, TargetSite


class ScrapebucketSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapebucketDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# Stealth-Selenium

from importlib import import_module
from shutil import which

import undetected_chromedriver as uc
from scrapy_selenium.middlewares import SeleniumMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumStealthMiddleware(SeleniumMiddleware):
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
        # driver_options = uc.ChromeOptions()

        if browser_executable_path:
            driver_options.binary_location = browser_executable_path
        for argument in driver_arguments:
            driver_options.add_argument(argument)

        driver_kwargs = {
            'executable_path': driver_executable_path,
            f'{driver_name}_options': driver_options,
        }

        driver_options.add_argument('--headless')
        driver_options.add_argument("--disable-blink-features=AutomationControlled")
        # driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # driver_options.add_experimental_option('useAutomationExtension', False)
        driver_options.add_argument('--disable-dev-shm-usage')
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--disable-gpu')
        driver_options.add_argument('--incognito')

        # stealth
        self.driver = driver_klass(**driver_kwargs)

        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor='Google Inc.',
            platform='Win32',
            webgl_vendor='Intel Inc.',
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )


# undetected_chromedriver setup for linux only
class UndetectedChromeDriver(SeleniumMiddleware):
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
        self.driver = uc.Chrome()


# Custom Middlewares


# Log Stats
class JobStatLogsMiddleware(object):
    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_closed(self, spider, reason):
        stats = spider.crawler.stats.get_stats()
        bot_name = spider.crawler.settings.get('BOT_NAME')

        domain_name = spider.domain_name.split('.')[0]

        try:
            target_site_pk = (
                TargetSite.objects.filter(site_id__exact=domain_name).first().pk
            )

            job_logs = {}
            job_logs['target_site_id'] = target_site_pk
            job_logs['spider_name'] = spider.name
            job_logs['allowed_domain'] = domain_name
            job_logs['items_scraped'] = stats.get('item_scraped_count')
            job_logs['items_dropped'] = stats.get('item_dropped_count')
            job_logs['finish_reason'] = stats.get('finish_reason')
            job_logs['request_count'] = stats.get('downloader/request_count')
            job_logs['status_count_200'] = stats.get(
                'downloader/response_status_count/200'
            )
            job_logs['start_timestamp'] = stats.get('start_time')
            job_logs['end_timestamp'] = stats.get('finish_time')
            job_logs['elapsed_time'] = self.dt_interval(
                stats.get('elapsed_time_seconds')
            )
            job_logs['elapsed_time_seconds'] = stats.get('elapsed_time_seconds')

            logs = SpiderLog(**job_logs)
            logs.save()

            print(
                {
                    'REMARK': 'Done Crawling',
                    'BOT': bot_name,
                    'SPIDER': spider.name,
                    'TARGET_SITE': domain_name,
                }
            )
            # send to ftp server thru middleware_ftp
        except AttributeError:
            pass

        # def elapsed_time():
        #     return [e.get('elapsed_time_seconds') for e in spider_stats[0]]

        # total_elapsed = reduce(lambda acc, cur: acc + cur, elapsed_time(), 0)

        # summary_stats = {
        #     'total_spiders': len(elapsed_time()),
        #     'total_elapsed_time': self.dt_interval(total_elapsed),
        #     'average_elapsed_time': self.dt_interval(total_elapsed / len(elapsed_time())),
        # }

    def convert_dt(self, dt):
        return (
            pytz.utc.localize(dt)
            .astimezone(pytz.timezone('US/Eastern'))
            .strftime('%Y-%m-%d %I:%M:%S')
        )
        # pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Pacific'))
        # pytz.utc.localize(dt).astimezone(pytz.timezone('US/Pacific')).strftime("%Y-%m-%d %I:%M:%S %p") <-- with AM/ PM

    def dt_interval(self, s):
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


# FTP VDP URLS
class VdpUrlsMiddleWare(object):
    def __init__(self, crawler):  # or __(self,stats)
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_closed(self, spider, reason):
        domain_name = spider.domain_name.split('.')[0]
        self.send_to_ftp(domain_name, spider)

    def send_to_ftp(self, pk, spider):
        try:
            scrapes = TargetSite.objects.filter(site_id=pk).first().scrapes.all()
        except AttributeError:
            return

        csvfile = io.StringIO()
        writer = csv.writer(csvfile)

        fieldnames = ['VIN', 'VDP URLS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # quoting=csv.QUOTE_ALL

        writer.writeheader()
        for item in scrapes.values():
            writer.writerow(
                {
                    'VIN': item.get('vin'),
                    'VDP URLS': item.get('vehicle_url'),
                }
            )

        ftp = FTP(os.environ.get('AIM_FTP_HOST'))
        ftp.login(os.environ.get('AIM_FTP_USER'), os.environ.get('AIM_FTP_PASS'))

        ftp.storbinary(
            f'STOR VDP_URLS_{pk}.csv', io.BytesIO(csvfile.getvalue().encode())
        )
        print(f'SENT TO FTP: VDP_URLS_{pk}.csv')
