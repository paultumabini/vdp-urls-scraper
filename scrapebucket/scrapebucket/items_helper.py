"""
Input processors for ``ScrapebucketItem`` (MapCompose chains in ``items.py``).

These run on raw spider output before persistence; keep them tolerant of ``None``
and non-string types where practical.
"""

import re
from urllib.parse import urlparse

# Tokens stripped from stock / image fields (theme-specific noise).
_STOCK_AND_IMAGE_NOISE = (
    '-100x100',
    'Stock:',
    'Stock #:',
    'Stock No:',
    '-new',
    '-167x93',
    'thumb_',
    '|',
)


def remove_char_from_str(val):
    """Remove known thumbnail and label fragments from a string field."""
    if val is None or not isinstance(val, str):
        return val
    value = val
    for token in _STOCK_AND_IMAGE_NOISE:
        value = value.replace(token, '')
    return value


def remove_trailing_spaces(value):
    """Collapse newlines/tabs when present; otherwise return unchanged."""
    if value is None or not isinstance(value, str):
        return value
    if re.search(r'[\n\t]', value):
        return re.sub(r'[\n\t]*', '', value).strip()
    return value


def remove_non_numeric(value):
    """
    Strip non-digits for price-like fields.

    Skips aggressive stripping when the string looks like a VIN fragment (``XB``,
    ``U``/``N``) or a decimal, so we do not destroy identifiers by accident.
    """
    if (
        isinstance(value, str)
        and 'XB' not in value
        and '.' not in value
        and 'U' not in value
        and 'N' not in value
    ):
        return (
            re.sub(r'[^0-9]', '', value) if any(char.isdigit() for char in value) else 0
        )
    return 0 if not value or value == '' else value


def extract_vin(value):
    """Best-effort VIN from messy text or slug-style URLs (last 17-char segment)."""
    if value is None:
        return value
    if not isinstance(value, str):
        value = str(value)
    if re.search(r'[\n\t/]', value):
        value = re.sub(r'[\n\t/]*', '', value).strip()
    last_segment = value.split('-')[-1]
    xtract_vin = last_segment if len(last_segment) == 17 else value

    for noise in ('VIN', ':', 'VIN:'):
        xtract_vin = xtract_vin.replace(noise, '')
    return xtract_vin


def set_category(value):
    if not value or not isinstance(value, str):
        return ''
    lower = value.lower()
    if 'used' in lower:
        return 'used'
    if 'new' in lower:
        return 'new'
    return ''


def extract_dname(url):
    """Flatten hostname for legacy per-dealer URL hacks (see ``process_vdp_url``)."""
    p = urlparse(url)
    domain = p.netloc
    for s in ('.', 'com', 'net', 'org'):
        domain = domain.replace(s, '')
    return domain


def process_vdp_url(url):
    """Apply dealer-specific URL fixes before storage or comparison."""
    if not url:
        return url
    dn = extract_dname(url)

    # Historic IIS/front-end quirk: insert '-' after scheme for these hosts.
    if dn in ('pothiermotors', 'eastviewchev', 'oldsgm'):
        index = url.rfind('//') + 1
        return url[:index] + '-' + url[index:]
    return url
