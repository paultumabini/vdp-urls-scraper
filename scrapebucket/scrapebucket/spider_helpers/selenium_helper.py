import re
from ast import Lambda
from functools import reduce
from shutil import which

import undetected_chromedriver as uc
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


class SeleniumHelper:
    def __init__(self, url, selector, wait_until):
        self.url = url
        self.selector = selector
        self.wait_until = wait_until

    def get_page_source(self):
        chrome_options = Options()
        # arguments to possibly ignore "handshake failed" errors
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')

        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--ignore-certificate-errors')

        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--incognito')

        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--verbose')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')

        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_path = which('chromedriver')
        s = Service(chrome_path)
        # driver = webdriver.Chrome(service=s, options=chrome_options)

        driver = uc.Chrome(options=chrome_options)

        # stealth(
        #     driver,
        #     languages=['en-US', 'en'],
        #     vendor='Google Inc.',
        #     platform='Win32',
        #     webgl_vendor='Intel Inc.',
        #     renderer="Intel Iris OpenGL Engine",
        #     fix_hairline=True,
        # )

        driver.get(self.url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, self.wait_until)))
        return driver

    def get_pagination(self):
        driver = self.get_page_source()

        print('MY Pages', Selector(text=driver.page_source).xpath(self.selector).getall())

        num_list = [int(float(num)) for num in Selector(text=driver.page_source).xpath(self.selector).getall()]

        return reduce(lambda a, b: a if a > b else b, num_list)

    def get_pagination_remove_text(self):
        driver = self.get_page_source()
        pages = [re.sub(r'[^0-9]', '', num)
                 for num in Selector(text=driver.page_source).xpath(self.selector).getall()][0][1:]
        return int(float(pages))
        # num_list = [int(n) for n in [re.sub(r'[^0-9]', '', num) for num in Selector(text=driver.page_source).xpath(self.selector).getall()][0]]
        # return reduce(lambda a, b: a if a > b else b, num_list)

        # num_list = [int(num.strip()) for num in Selector(text=driver.page_source).xpath(self.selector).getall()]
        # return reduce(lambda a, b: a if a > b else b, num_list)


# result = SeleniumHelper(
#     'https://amford.com/NewFordInventory',
#     '//a[@class="vehicleTitleLink]/@href',
#     '//a[@class="vehicleTitleLink"]',
# )
# page = result.get_page_source()

# text = Selector(text=page.page_source).xpath('//a[@class="vehicleTitleLink]/@href').getall()

# print(page)
