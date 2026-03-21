import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import django

sys.path.append(os.path.join(Path(__file__).parents[4], 'webscraping'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'webscraping.settings'
django.setup()

from project.models import TargetSite


def get_company_id(domain):
    try:
        company_id = TargetSite.objects.get(site_id=domain).feed_id
    except TargetSite.DoesNotExist:
        company_id = None
    return company_id


# previous method at server-side access to PHP file
def parse_trader_url(url, id, page, num):
    parsed_qs = {
        'endpoint': [
            f'https://vms.prod.convertus.rocks/api/filtering/?cp={id}&ln=en&pg={page}&pc={num}'
        ],
        'action': ['vms_data'],
    }
    encoded_qs = urlencode(parsed_qs, doseq=1)
    new_url = f'{url}wp-content/plugins/convertus-vms/include/php/ajax-vehicles.php?{encoded_qs}'
    return new_url


# current method via direct API
def access_trader_direct_API(id, page, num):
    url_api = f'https://vms.prod.convertus.rocks/api/filtering/?cp={id}&ln=en&pg={page}&pc={num}'
    return url_api


def keep_top_lvl_domain(dname):
    # Use regular expression to replace all but the last dot with an empty string
    modified_string = re.sub(r'\.(?=[^.]*\.)', '', dname)
    return modified_string
