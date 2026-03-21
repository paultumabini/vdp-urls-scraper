"""
    References:
    `updated google sheets with data`
    https://developers.google.com/sheets/api/quickstart/python
    https://developers.google.com/identity/protocols/oauth2/service-account#python
    https://developers.google.com/sheets/api/reference/rest
"""


from project.models import AimDealer, Webprovider
from django.contrib.auth.models import User
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import django
import numpy as np
import pandas as pd
import requests
from django.db import IntegrityError
# from django.utils import timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# append path to the project dir
sys.path.append(os.path.join(Path(__file__).parents[3], 'webscraping'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'webscraping.settings'
django.setup()


class GsApiData:
    def __init__(self, safile, scopes, ssid):
        self._SERVICE_ACCOUNT_FILE = safile
        self._SCOPES = scopes
        self._SPREADSHEET_ID = ssid

    @property
    def serv_acct_file(self):
        return self._SERVICE_ACCOUNT_FILE

    @serv_acct_file.setter
    def serv_acct_file(self, file):
        if not self._SERVICE_ACCOUNT_FILE:
            self._SERVICE_ACCOUNT_FILE = file

    @property
    def scopes(self):
        return self._SCOPES

    @scopes.setter
    def scopes(self, scopes):
        if not self._SCOPES:
            self._SCOPES = scopes

    @property
    def ss_id(self):
        return self._SPREADSHEET_ID

    @ss_id.setter
    def ss_id(self, id):
        if not self._SPREADSHEET_ID:
            self._SPREADSHEET_ID = id

    @classmethod
    def from_get_credentials(cls, safile, scopes, ssid):
        return cls(safile, scopes, ssid)

    @classmethod
    def access_gs_api(cls, creds=None, **kwargs):
        if not creds:
            creds = service_account.Credentials.from_service_account_file(
                kwargs['_SERVICE_ACCOUNT_FILE'], scopes=kwargs['_SCOPES'])

        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            # Read sheet values
            result = sheet.values().get(spreadsheetId=kwargs['_SPREADSHEET_ID'], range='dealers_list!A2:T').execute()
            values = result.get('values', [])

            # AimDealer.objects.all().delete()
            # Webprovider.objects.all().delete()

            # convert values into dataframe
            df = pd.DataFrame(values)
            # target columns
            df = df.iloc[:, np.r_[0:6]]
            # replace all non trailing blank values created by GS API
            # with null values
            df_replace = df.replace([''], [None])

            # convert back to list to insert into Redshift
            processed_dataset = df_replace.values.tolist()

            # print(processed_dataset)

            if not processed_dataset:
                print('No data found -', processed_dataset)
                return

            keys = [f.get_attname() for f in AimDealer._meta.fields][0:-4]

            list_of_dic = [dict(zip(keys, value)) for value in processed_dataset]

            # filter out web_provider_id
            # example web_provider_id != **AVO
            excluded_value_list = ['**AVO', None]
            filtered_list = [d for d in list_of_dic if d['web_provider_id'] not in excluded_value_list]

            # print(filtered_list)
            return filtered_list

        except HttpError as err:
            print(err)

    @classmethod
    def render_gs_data(cls, data):

        for data in [dic.items() for dic in data]:
            obj = {}

            for key, value in data:
                if key == 'web_provider_id':
                    value = re.sub('[^A-Za-z0-9]+', '', value).lower() if value else 'WALA PA'

                    # get or create additional web providers
                    Webprovider.objects.get_or_create(name=value)
                    # value = Webprovider.objects.filter(name=value).first().id

                obj[key] = value

            # `get_or_create` preserves if does exist otherwise create
            # if Dealer is using custom pk, e.g. dealer_id if already existing and
            # trying to save same id, it will throw error. use Object(**kwargs).save()
            # instead to force save.

            try:
                dealer, created = AimDealer.objects.get_or_create(
                    account=obj.get('account'),
                    dealer_id=obj.get('dealer_id'),
                    dealer_name=obj.get('dealer_name'),
                    site_url=obj.get('site_url'),
                    web_provider=Webprovider.objects.get(name=obj.get('web_provider_id')),
                    account_manager=obj.get('account_manager'),
                    author=User.objects.first(),
                )
                print(dealer, created)
            except IntegrityError:
                pass


gs = GsApiData
safile = gs.serv_acct_file = '/home/pt/Dev/Projects/django/aim/vdp/vdpimporthelper/vdpurls/utils/keys_gs.json'
scopes = gs.scopes = ['https://www.googleapis.com/auth/spreadsheets']
ssid = gs.ss_id = '1UZ5V28_nCZaNLq9CITviqOzM0_5xpvjn3iSkvATC9LI'
res = gs.from_get_credentials(safile, scopes, ssid)
data = gs.access_gs_api(**vars(res))
gs.render_gs_data(data)


# !NOTE: ERRORS MAY OCCUR LIKE THIS BELOW. Please make sure outside VM VPN is OFF or internal nerwork is up and running
# File
# "/home/pt/Dev/Projects/django/aim/scrape/venv/lib/python3.11/site-packages/google_auth_httplib2.py",
# line 126, in __call__    raise exceptions.TransportError(exc)
# google.auth.exceptions.TransportError: Unable to find the server at
# oauth2.googleapis.com
