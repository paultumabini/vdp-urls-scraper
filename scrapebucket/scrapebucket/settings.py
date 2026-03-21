# Scrapy settings for scrapebucket project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapebucket'

DOMAIN_NAME = ''

SPIDER_MODULES = ['scrapebucket.spiders']
NEWSPIDER_MODULE = 'scrapebucket.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'scrapebucket.middlewares.ScrapebucketSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapebucket.pipelines.ScrapebucketPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 2  # 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 6  # 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# =======================[ SELENIUM ]================================
from shutil import which

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

chrome_path = which('chromedriver')

# webdriver.Chrome(
#     # solution:Message: 'FOR LINUX: chromedriver' executable needs to be in PATH #
#     service=ChromeService(ChromeDriverManager().install()),
# )

SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_EXECUTABLE_PATH = '/home/pt/Dev/Projects/django/aim/webscraping/scrapebucket/chromedriver'
# SELENIUM_DRIVER_ARGUMENTS = ['--headless']  # '--headless' if using chrome instead of firefox
# DOWNLOADER_MIDDLEWARES = {'scrapebucket.middlewares.SeleniumStealthMiddleware': 300}


SPIDER_MIDDLEWARES = {
    'scrapebucket.middlewares.JobStatLogsMiddleware': 300,
    'scrapebucket.middlewares.VdpUrlsMiddleWare': 300,
}


FEED_EXPORT_ENCODING = 'utf-8'
DOWNLOAD_FAIL_ON_DATALOSS = False
RETRY_ENABLED = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# =======================[ Limit/close spider crawl at specific item count ]=======================
# 'CLOSESPIDER_ITEMCOUNT': 10,

# =======================[ set path/ directory ]=======================
# FILES_STORE = 'D:\\MyProjects\\web_scraping\\aimexperts\\scrapebucket\\files_output'
# IMAGES_STORE = 'D:\\MyProjects\\web_scraping\\aimexperts\\scrapebucket\\files_output'

# =======================[ FOR TESTING  ]=======================
# custom_settings = {
#     # 'ITEM_PIPELINES': {'scrapebucket.pipelines.McdonaldGmPipeline': 300},
#     'DOWNLOADER_MIDDLEWARES': {'scrapebucket.middlewares.ScrapebucketDownloaderMiddleware': 543},
#     'SPIDER_MIDDLEWARES': {
#         'scrapebucket.middlewares.ScrapebucketSpiderMiddleware': 543,
#     },
# }
