"""
URL/query helpers for spiders (Convertus VMS and domain utilities).

Depends on Django ORM via ``ensure_django()`` for ``TargetSite`` lookups.
"""

from __future__ import annotations

import re
from urllib.parse import urlencode

from ..django_setup import ensure_django

ensure_django()

from project.models import TargetSite


def get_company_id(domain: str) -> str | None:
    """Return ``TargetSite.feed_id`` for a site id / domain key, or ``None``."""
    try:
        return TargetSite.objects.get(site_id=domain).feed_id
    except TargetSite.DoesNotExist:
        return None


def parse_trader_url(url: str, id_: str, page: int, num: int) -> str:
    """Legacy PHP proxy URL for Convertus VMS (server-side plugin endpoint)."""
    parsed_qs = {
        'endpoint': [
            f'https://vms.prod.convertus.rocks/api/filtering/?cp={id_}&ln=en&pg={page}&pc={num}'
        ],
        'action': ['vms_data'],
    }
    encoded_qs = urlencode(parsed_qs, doseq=True)
    return (
        f'{url}wp-content/plugins/convertus-vms/include/php/ajax-vehicles.php?'
        f'{encoded_qs}'
    )


def access_trader_direct_api(id_: str, page: int, num: int) -> str:
    """Direct Convertus VMS filtering API URL (preferred over ``parse_trader_url``)."""
    return (
        f'https://vms.prod.convertus.rocks/api/filtering/'
        f'?cp={id_}&ln=en&pg={page}&pc={num}'
    )


# Backwards-compatible alias (historical typo: API vs Api).
access_trader_direct_API = access_trader_direct_api


def keep_top_lvl_domain(dname: str) -> str:
    """Collapse subdomain labels so only the registrable-style host remains."""
    return re.sub(r'\.(?=[^.]*\.)', '', dname)
