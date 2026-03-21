from scrapy import spiderloader

# Models
# sys.path.insert(0, 'D:\\MyProjects\\django\webscraping_project\\webscraping')
# sys.path.append(r'D:\MyProjects\django\webscraping_project\webscraping') # <-- OR below:
# sys.path.append(os.path.join(Path(__file__).parents[4], 'webscraping'))  # root directory
# os.environ['DJANGO_SETTINGS_MODULE'] = 'webscraping.settings'
# django.setup()


# prepare crawlers with their corresponding target urls into a list i.e,  [<spider>, <url>]
def get_urls(sites, classes):
    for spider, class_name in classes:
        objects = sites.objects.filter(spider=spider).all()
        for obj in objects:
            if obj.spider == spider:
                yield [class_name, obj.site_url, obj.site_id, obj.status]


# get all spiders and spider classes
def match_spiders(target_sites, settings):
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    spider_classes = [[name, spider_loader.load(name)] for name in spiders]
    yield get_urls(target_sites, spider_classes)


# Spiders
"""
Spider Hints:

AutobunnySpider: scrapy.Request, LINKEXTRACTOR
DealerinspireSpider: SeleniumRequest, selenium_stealth, selenium_helper
LynxdigitalSpider: CrawlSpider, scrapy.Request
NabthatSpider: scrapy.Request, API
SeowindsorSpider: scrapy.Request, API



Notes:

The difference of running the file and spider name has underscore ('_'). For example, av_motors:

$ scrapy crawl av_motors -a url=https://www.griffithsford.ca/
$ python runspider.py -s avmotors

"""
# results = match_spiders(target_sites_model, settings)

# for res in results:
#     print(res)
#     for a, b in res:
#         print(a, b)
