"""
Safe JSON decoding for Scrapy (and binary API) bodies.

Callers should treat ``None`` as "drop this response / skip parse" — upstream may return
HTML error pages, empty bodies, or non-UTF8 bytes even when ``Content-Type`` claims JSON.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def loads_response_body(
    body: bytes,
    *,
    url: str = '',
    label: str = 'spider',
) -> Any | None:
    try:
        return json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as exc:
        # Warning (not error): spiders often see flaky dealer CDNs; log and continue.
        logger.warning('%s: invalid JSON from %s: %s', label, url or '(no url)', exc)
        return None
