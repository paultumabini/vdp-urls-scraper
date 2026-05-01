"""
Initialize Django once for all Scrapy code paths that use the ORM.

Walks parent directories until ``manage.py`` is found, prepends that directory to
``sys.path``, sets required environment variables, then calls ``django.setup()``.

Idempotent: subsequent calls are no-ops guarded by ``_CONFIGURED``.  Call sites
(``settings.py``, middlewares, pipelines, ``runspider.py``) can all call
``ensure_django()`` safely without risking double-initialisation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_CONFIGURED = False


def ensure_django() -> None:
    """Locate the Django project root, patch ``sys.path``, and run ``django.setup()``."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    here = Path(__file__).resolve()
    project_root: Path | None = None
    for parent in here.parents:
        if (parent / 'manage.py').exists():
            project_root = parent
            break

    if project_root is None:
        raise RuntimeError(
            'Cannot locate Django project: no manage.py found in parents of '
            f'{here}'
        )

    root_str = str(project_root)
    if root_str not in sys.path:
        # Prepend so repo packages (e.g. ``webscraping``) shadow same-named site-packages.
        sys.path.insert(0, root_str)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')
    # Required for synchronous ORM access inside Twisted/async contexts (Playwright
    # spiders, spider_closed signals).  Prefer sync_to_async in new code.
    os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')

    import django

    django.setup()
    _CONFIGURED = True
