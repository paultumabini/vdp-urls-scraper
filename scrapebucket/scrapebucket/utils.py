"""
Dealer-specific URL builders and cookie helpers (O'Regans / legacy Autotrader-style flows).

``request_all_urls`` performs live HTTP on import/call sites — use only from trusted runners;
prefer timeouts and explicit error handling when wiring new spiders.
"""

from __future__ import annotations

import json
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlencode, urlparse

import requests

# --- O'Regans CDN API templates (lot + widget profile embedded in query string) ---
URL_HALIFAX_NISSAN = 'https://oserv3.oreganscdn.com/api/vehicle-inventory-search/?search.vehicle-inventory-type-ids.0=&search.vehicle-make-ids.0=35&search.min-mileage=&search.max-mileage=&search.min-year=&search.max-year=&search.min-price=&search.max-price=&search.lot-location-ids.0=3&search.stock-number=&search.vin=&search.beta=&search.sort-order=newest&do-search=1&search.results-offset=0&search.results-limit=1&app.widgetProfile.id=5626e7e6-430b-41dc-a52c-3a425f529ee1.searchResults.search&app.referrer=https%3A%2F%2Fwww.oregansnissanhalifax.com%2Finventory%2F%3Fdo-search%3D1'

URL_DARTMOUTH_NISSAN = 'https://oserv3.oreganscdn.com/api/vehicle-inventory-search/?search.vehicle-inventory-type-ids.0=&search.vehicle-make-ids.0=35&search.min-mileage=&search.max-mileage=&search.min-year=&search.max-year=&search.min-price=&search.max-price=&search.lot-location-ids.0=17&search.stock-number=&search.vin=&search.beta=&search.sort-order=newest&do-search=1&search.results-offset=0&search.results-limit=10&app.widgetProfile.id=5626e7e6-430b-41dc-a52c-3a425f529ee1.searchResults.search&app.referrer=https%3A%2F%2Fwww.oregansnissandartmouth.com%2Finventory%2F%3Fdo-search%3D1'

URL_HALIFAX_KIA = 'https://oserv3.oreganscdn.com/api/vehicle-inventory-search/?search.vehicle-inventory-type-ids.0=&search.vehicle-make-ids.0=24&search.min-mileage=&search.max-mileage=&search.min-year=&search.max-year=&search.min-price=&search.max-price=&search.lot-location-ids.0=15&search.stock-number=&search.vin=&search.beta=&search.sort-order=newest&do-search=1&search.results-offset=0&search.results-limit=10&app.widgetProfile.id=5626e7e6-430b-41dc-a52c-3a425f529ee1.searchResults.search&app.referrer=https%3A%2F%2Fwww.oreganskiahalifax.com%2Finventory%2F%3Fdo-search%3D1'

URL_DARTMOUTH_KIA = 'https://oserv3.oreganscdn.com/api/vehicle-inventory-search/?search.vehicle-inventory-type-ids.0=&search.vehicle-make-ids.0=24&search.min-mileage=&search.max-mileage=&search.min-year=&search.max-year=&search.min-price=&search.max-price=&search.lot-location-ids.0=6&search.stock-number=&search.vin=&search.beta=&search.sort-order=newest&do-search=1&search.results-offset=0&search.results-limit=10&app.widgetProfile.id=5626e7e6-430b-41dc-a52c-3a425f529ee1.searchResults.search&app.referrer=https%3A%2F%2Fwww.oreganskiadartmouth.com%2Finventory%2F%3Fdo-search%3D1'

# Example ``Cookie`` header strings from past sessions (prefer fresh cookies per crawl).
COOKIE_NOVLANBROS = 'is_mobile=No; _ga=GA1.2.823608099.1642443282; _gid=GA1.2.2147296910.1642443282; mf_uuid=603b286b-0c69-49a9-a9e0-f48786920ea3; aavdpnew=/inventory/details/; aavdpused=/inventory/details/; aass=; aasrpnew=[New%; aasrpused=[Used%; aasrpss=cmV0dXJuICIi; aavs=; aasrpvs=cmV0dXJuICIi; aasrpvc=; smc=.1642443310618.1431; mmc=c57f803a-05b7-44f0-806d-0b6af331e660; _gat_gtag_UA_50977265_1=1'

COOKIE_STANDARDDODGE = 'is_mobile=No; _ga=GA1.2.1636430230.1644279379; _gid=GA1.2.1887157072.1644279379; smedia_uuid=a040118ffb265eb031c1c22af8bf10088aae593343bee25d179f915ed59751fa; av-platform={"queuedEvents":[{"tag":"AV Platform","value":"av lead tracker initialized","timestamp":1644279401215,"gclid":"1636430230.1644279379"},{"tag":"AV Platform","value":"utm data is set","timestamp":1644279401216,"gclid":"1636430230.1644279379"}],"utm":{"source":null,"medium":null,"campaign":null,"term":null,"content":null},"googleClientId":"1636430230.1644279379","landingPageUrl":"https://standarddodge.ca/"}; _fbp=fb.1.1644279423559.1957402944; _gat_gtag_UA_1341196_30=1; _gat_gtag_UA_196760063_34=1; smedia_session_id=76b1f83db772e382f99af9c4a5d9ca5323abc1b6f4f591c1937b9afe2e0cc39a'


def get_result_offset(url):
    """Parse ``search.results-offset`` from an O'Regans API URL (default 0)."""
    query_string = parse_qs(urlparse(url).query)
    raw = query_string.get('search.results-offset', ['0'])[0]
    return int(raw)


def parse_new_url(url, offset, limit, url_api):
    """Clone query string with new offset/limit; ``url_api`` is scheme+netloc+path prefix."""
    query_string = parse_qs(urlparse(url).query)
    query_string['search.results-offset'] = [str(offset)]
    query_string['search.results-limit'] = [str(limit)]
    encoded_qs = urlencode(query_string, doseq=True)
    return f'{url_api}{encoded_qs}'


def request_all_urls(domain, url_api, *, timeout=30):
    """
    Build paginated O'Regans API URLs from an initial template and total count.

    The first request uses a small limit to read ``totalResultsCount``; subsequent
    URLs walk offsets in ``initial_search_limit`` steps (legacy pagination logic).
    """
    url_map = {
        'oregansnissanhalifax.com': URL_HALIFAX_NISSAN,
        'oregansnissandartmouth.com': URL_DARTMOUTH_NISSAN,
        'oreganskiahalifax.com': URL_HALIFAX_KIA,
        'oreganskiadartmouth.com': URL_DARTMOUTH_KIA,
    }
    URL = url_map.get(domain, '')
    if not URL:
        return []

    initial_search_limit = 10
    try:
        res = requests.get(URL, timeout=timeout)
        res.raise_for_status()
        payload = res.json()
    except (requests.RequestException, json.JSONDecodeError, ValueError):
        return []

    results = payload.get('search') or {}
    stats = results.get('stats') or {}
    total_raw = stats.get('totalResultsCount')
    if total_raw is None:
        return []
    total_units = int(total_raw)

    # Original code always took the “float division” branch in Python 3; keep +3 slack.
    rng = (total_units // initial_search_limit) + 3

    request_url = URL
    request_url_list = []
    count = 0

    for i in range(rng):
        initial_search_offset = get_result_offset(request_url)

        if initial_search_offset == 0 and count == 0:
            search_offset = 0
            search_limit = 1
            count += 1
        elif initial_search_offset == 0 and count == 1:
            search_offset = 1
            search_limit = initial_search_limit
        elif initial_search_offset >= 1 and i < rng - 1:
            search_offset = initial_search_offset + initial_search_limit
            search_limit = initial_search_limit
        else:
            search_offset = initial_search_offset + (total_units % initial_search_limit) - 1
            search_limit = initial_search_limit

        request_url = parse_new_url(request_url, search_offset, search_limit, url_api)
        request_url_list.append(request_url)

    return request_url_list


def cookie_parser(c):
    """Parse a ``Cookie`` header string into a dict for ``requests`` / Scrapy."""
    cookie = SimpleCookie()
    cookie.load(c)
    return {k: morsel.value for k, morsel in cookie.items()}
