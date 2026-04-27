"""
Initialize Django once for Scrapy code paths that use the ORM (e.g. ``TargetSite``).

Walks parents of this file until ``manage.py`` is found, prepends that directory to
``sys.path``, then runs ``django.setup()``. Safe to call from multiple helpers; the
second call is a no-op.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_CONFIGURED = False


def ensure_django() -> None:
    """Add project root to ``sys.path`` and run ``django.setup()``."""
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
        # Prepend so repo packages (e.g. ``webscraping``) win over same-named site-packages.
        sys.path.insert(0, root_str)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')

    import django

    django.setup()
    _CONFIGURED = True
