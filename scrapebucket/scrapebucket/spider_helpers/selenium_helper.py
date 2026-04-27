"""
Synchronous Selenium helpers for pagination / page source (undetected-chromedriver).
"""

from __future__ import annotations

import logging
import re
from functools import reduce

import undetected_chromedriver as uc
from scrapy.selector import Selector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class SeleniumHelper:
    """Headless Chrome: load URL, wait for selector, scrape pagination hints."""

    def __init__(self, url: str, selector: str, wait_until: str):
        self.url = url
        self.selector = selector
        self.wait_until = wait_until

    def _build_options(self) -> Options:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        return chrome_options

    def get_page_source(self):
        chrome_options = self._build_options()
        driver = None
        try:
            driver = uc.Chrome(options=chrome_options)
            driver.get(self.url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, self.wait_until))
            )
            return driver
        except Exception:
            if driver is not None:
                driver.quit()
            raise

    def get_pagination(self) -> int:
        driver = self.get_page_source()
        try:
            sel = Selector(text=driver.page_source)
            raw = sel.xpath(self.selector).getall()
            logger.debug('Pagination raw values: %s', raw)
            num_list = [int(float(n)) for n in raw]
            if not num_list:
                return 1
            return reduce(lambda a, b: a if a > b else b, num_list)
        finally:
            driver.quit()

    def get_pagination_remove_text(self) -> int:
        driver = self.get_page_source()
        try:
            sel = Selector(text=driver.page_source)
            nodes = sel.xpath(self.selector).getall()
            if not nodes:
                return 1
            digits = re.sub(r'[^0-9]', '', nodes[0] or '')
            if not digits:
                return 1
            # Legacy behaviour: drop first digit char then parse (site-specific).
            tail = digits[1:] if len(digits) > 1 else digits
            return int(float(tail))
        finally:
            driver.quit()
