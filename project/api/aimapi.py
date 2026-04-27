"""
Sync AIM dealer account status from the external AIM Admin API into ``AimDealer``.

Run as a management-style script (not imported by the web app):

    DJANGO_SETTINGS_MODULE=webscraping.settings python -m project.api.aimapi

Environment:

- ``AVAIM_EMAIL`` / ``AVAIM_PASS`` — API credentials (required to run).
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import django
import requests

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = (10, 60)


def _bootstrap_django() -> None:
    repo_webscraping = Path(__file__).resolve().parents[2]
    if str(repo_webscraping) not in sys.path:
        sys.path.insert(0, str(repo_webscraping))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')
    django.setup()


class AimApiData:
    """Thin client for AIM auth + dealer list; updates local ``AimDealer.account``."""

    _login_url = 'https://aim-admin.com/ncso_api/auth'
    _status_url = 'https://aim-admin.com/aim_system_api/get_data_for_dealers_page/'

    def __init__(self, email: str | None, password: str | None):
        self._email = email
        self._password = password

    @property
    def email(self) -> str | None:
        return self._email

    @email.setter
    def email(self, value: str | None) -> None:
        self._email = value

    @property
    def password(self) -> str | None:
        return self._password

    @password.setter
    def password(self, value: str | None) -> None:
        self._password = value

    @classmethod
    def from_get_credentials(cls, email: str | None, password: str | None) -> AimApiData:
        return cls(email, password)

    @classmethod
    def access_aim_api(cls, **kwargs) -> list | None:
        email, password = kwargs.get('_email'), kwargs.get('_password')
        if not email or not password:
            logger.error('AVAIM_EMAIL and AVAIM_PASS must be set.')
            return None

        form_data = {
            'email': email,
            'password': password,
            'last_logged_version': 'aim_admin',
            'extra_info': {
                'login_type': 0,
                'os': 'Windows',
                'device': 'chrome 107.0.0.0',
            },
        }

        login_res = requests.post(
            cls._login_url, json=form_data, timeout=_REQUEST_TIMEOUT
        )
        login_res.raise_for_status()
        login_payload = login_res.json()
        if not isinstance(login_payload, list) or len(login_payload) < 2:
            logger.error('Unexpected login response shape from AIM API.')
            return None

        session_id = login_payload[1].get('session_id')
        if not session_id:
            logger.error('No session_id in AIM login response.')
            return None

        status_res = requests.get(
            f'{cls._status_url}{session_id}',
            timeout=_REQUEST_TIMEOUT,
        )
        status_res.raise_for_status()
        status_payload = status_res.json()
        if not isinstance(status_payload, list) or len(status_payload) < 2:
            logger.error('Unexpected status response shape from AIM API.')
            return None

        return status_payload[1].get('data')

    @classmethod
    def render_api_data(cls, aimdata: list | None) -> None:
        if not aimdata:
            logger.warning('No dealer rows from AIM API; skipping DB update.')
            return

        from django.db.models import CharField
        from django.db.models.functions import Cast

        from project.models import AimDealer

        updated = 0
        for dealer in aimdata:
            ext_id = dealer.get('id')
            account = dealer.get('account')
            if ext_id is None or account is None:
                continue
            try:
                row = AimDealer.objects.annotate(
                    id_str=Cast('dealer_id', output_field=CharField())
                ).get(id_str=str(ext_id))
            except AimDealer.DoesNotExist:
                logger.debug('No local AimDealer for external id %s', ext_id)
                continue
            except AimDealer.MultipleObjectsReturned:
                logger.warning('Multiple AimDealer rows for external id %s', ext_id)
                continue

            if row.account != account:
                row.account = account
                row.save(update_fields=['account'])
                updated += 1

        logger.info(
            'AIM account sync finished: updated %s dealers (total local: %s).',
            updated,
            AimDealer.objects.count(),
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    _bootstrap_django()

    credential = AimApiData.from_get_credentials(
        os.environ.get('AVAIM_EMAIL'),
        os.environ.get('AVAIM_PASS'),
    )
    res_data = AimApiData.access_aim_api(**vars(credential))
    AimApiData.render_api_data(res_data)


if __name__ == '__main__':
    main()
