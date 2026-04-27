"""
Import dealer rows from a Google Sheet into ``AimDealer`` / ``Webprovider``.

Run as a script (not imported by the web app):

    DJANGO_SETTINGS_MODULE=webscraping.settings python -m project.api.gsapi

Environment (optional overrides for defaults below):

- ``GS_SERVICE_ACCOUNT_FILE`` — path to service account JSON.
- ``GS_SPREADSHEET_ID`` — spreadsheet id.
- ``GS_SHEET_RANGE`` — A1 range (default ``dealers_list!A2:T``).

Requires VPN/network access to Google APIs; transport errors usually mean DNS or firewall.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

import django
import numpy as np
import pandas as pd
from django.db import IntegrityError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

_DEFAULT_SA_PATH = (
    '/home/pt/Dev/Projects/django/aim/vdp/vdpimporthelper/vdpurls/utils/keys_gs.json'
)
_DEFAULT_SPREADSHEET_ID = '1UZ5V28_nCZaNLq9CITviqOzM0_5xpvjn3iSkvATC9LI'
_DEFAULT_RANGE = 'dealers_list!A2:T'
_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
_EXCLUDED_WEB_PROVIDERS = frozenset({'**AVO', None})


def _bootstrap_django() -> None:
    repo_webscraping = Path(__file__).resolve().parents[2]
    if str(repo_webscraping) not in sys.path:
        sys.path.insert(0, str(repo_webscraping))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webscraping.settings')
    django.setup()


class GsApiData:
    """Read normalized rows from Sheets and upsert dealers."""

    def __init__(self, safile: str, scopes: list[str], ssid: str):
        self._SERVICE_ACCOUNT_FILE = safile
        self._SCOPES = scopes
        self._SPREADSHEET_ID = ssid

    @property
    def serv_acct_file(self) -> str:
        return self._SERVICE_ACCOUNT_FILE

    @serv_acct_file.setter
    def serv_acct_file(self, file: str) -> None:
        if not self._SERVICE_ACCOUNT_FILE:
            self._SERVICE_ACCOUNT_FILE = file

    @property
    def scopes(self) -> list[str]:
        return self._SCOPES

    @scopes.setter
    def scopes(self, scopes: list[str]) -> None:
        if not self._SCOPES:
            self._SCOPES = scopes

    @property
    def ss_id(self) -> str:
        return self._SPREADSHEET_ID

    @ss_id.setter
    def ss_id(self, id_: str) -> None:
        if not self._SPREADSHEET_ID:
            self._SPREADSHEET_ID = id_

    @classmethod
    def from_get_credentials(cls, safile: str, scopes: list[str], ssid: str) -> GsApiData:
        return cls(safile, scopes, ssid)

    @classmethod
    def access_gs_api(
        cls,
        creds=None,
        *,
        range_a1: str = _DEFAULT_RANGE,
        **kwargs,
    ) -> list[dict] | None:
        sa_path = kwargs['_SERVICE_ACCOUNT_FILE']
        sheet_id = kwargs['_SPREADSHEET_ID']
        sheet_scopes = kwargs['_SCOPES']

        if not creds:
            creds = service_account.Credentials.from_service_account_file(
                sa_path, scopes=sheet_scopes
            )

        from project.models import AimDealer

        try:
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range=range_a1,
            ).execute()
            values = result.get('values', [])

            df = pd.DataFrame(values)
            if df.empty:
                logger.warning('Google Sheet range returned no rows.')
                return None

            df = df.iloc[:, np.r_[0:6]]
            df_replace = df.replace([''], [None])
            processed_dataset = df_replace.values.tolist()

            if not processed_dataset:
                logger.warning('No data after normalizing sheet rows.')
                return None

            # Align with AimDealer columns (exclude trailing audit FKs, etc.).
            keys = [f.get_attname() for f in AimDealer._meta.fields][0:-4]
            list_of_dic = [dict(zip(keys, value)) for value in processed_dataset]

            filtered_list = [
                d
                for d in list_of_dic
                if d.get('web_provider_id') not in _EXCLUDED_WEB_PROVIDERS
            ]
            return filtered_list

        except HttpError as err:
            logger.error('Google Sheets API error: %s', err)
            return None

    @classmethod
    def render_gs_data(cls, data: list[dict] | None) -> None:
        if not data:
            logger.warning('No rows to import.')
            return

        from django.contrib.auth.models import User

        from project.models import AimDealer, Webprovider

        author = User.objects.order_by('pk').first()
        created_count = 0
        skipped = 0

        for row in data:
            obj = {}
            for key, value in row.items():
                if key == 'web_provider_id':
                    slug = (
                        re.sub('[^A-Za-z0-9]+', '', value).lower()
                        if value
                        else 'WALA PA'
                    )
                    Webprovider.objects.get_or_create(name=slug)
                    obj[key] = slug
                else:
                    obj[key] = value

            provider_name = obj.get('web_provider_id')
            try:
                wp = Webprovider.objects.get(name=provider_name)
            except Webprovider.DoesNotExist:
                logger.debug('Skip row: web provider %r missing.', provider_name)
                skipped += 1
                continue

            dealer_id = obj.get('dealer_id')
            if dealer_id is None:
                skipped += 1
                continue
            try:
                _, created = AimDealer.objects.get_or_create(
                    dealer_id=dealer_id,
                    defaults={
                        'account': obj.get('account'),
                        'dealer_name': obj.get('dealer_name'),
                        'site_url': obj.get('site_url'),
                        'web_provider': wp,
                        'account_manager': obj.get('account_manager'),
                        'author': author,
                    },
                )
                if created:
                    created_count += 1
            except IntegrityError:
                skipped += 1
                logger.debug(
                    'IntegrityError for dealer_id=%s; skipped.',
                    dealer_id,
                )

        logger.info(
            'Sheet import finished: %s new dealers, %s rows skipped/errors.',
            created_count,
            skipped,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    _bootstrap_django()

    safile = os.environ.get('GS_SERVICE_ACCOUNT_FILE', _DEFAULT_SA_PATH)
    ssid = os.environ.get('GS_SPREADSHEET_ID', _DEFAULT_SPREADSHEET_ID)
    range_a1 = os.environ.get('GS_SHEET_RANGE', _DEFAULT_RANGE)

    res = GsApiData.from_get_credentials(safile, _SCOPES, ssid)
    data = GsApiData.access_gs_api(range_a1=range_a1, **vars(res))
    GsApiData.render_gs_data(data)


if __name__ == '__main__':
    main()
