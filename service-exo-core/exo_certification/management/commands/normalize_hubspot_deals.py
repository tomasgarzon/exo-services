import json
import logging
import time
import urllib

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from rest_framework import status

from ...helpers.hubspot import normalize_deal_name, hubspot_timestamp_to_date

logger = logging.getLogger('hubspot')

API_ROOT_URL = 'https://api.hubapi.com/'
API_LAPSE = 0.25


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--pipeline', nargs='+', type=str,
            help=''
        )

    def get_contact(self, vid):
        url = '{}contacts/v1/contact/vid/{}/profile?hapikey={}'.format(
            API_ROOT_URL,
            vid,
            settings.HAPIKEY,
        )
        response = requests.get(url=url, headers={})
        time.sleep(API_LAPSE)
        try:
            assert status.is_success(response.status_code)
        except AssertionError:
            logger.info('ERROR: normalize_hubspot_deals: Contact with vid {} does not exist'.format(vid))
            return None

        properties = response.json().get('properties')
        contact = ''
        if properties.get('full_name', None):
            contact += '{} '.format(properties['full_name']['value'])
        contact += properties['email']['value']

        return contact

    def normalize_deal(self, deal_id, pipeline):
        url = '{}deals/v1/deal/{}?hapikey={}'.format(
            API_ROOT_URL,
            deal_id,
            settings.HAPIKEY,
        )
        response = requests.get(url=url, headers={})
        time.sleep(API_LAPSE)

        try:
            assert status.is_success(response.status_code)
        except AssertionError:
            logger.info(
                'ERROR: normalize_hubspot_deals: Could not get Deal {} - Request status code [{}]'.format(
                    deal_id, response.status_code)
            )
            return False

        deal = response.json()
        try:
            properties = deal['properties']
            if properties['pipeline']['value'] == pipeline:
                contact = self.get_contact(deal['associations']['associatedVids'][0])
                if contact:
                    timestamp = None
                    lang = None
                    if properties.get('certification_program', None):
                        timestamp = hubspot_timestamp_to_date(
                            properties['certification_program']['value'])
                    if properties.get('certification_language', None):
                        lang = properties['certification_language']['value']

                    name = normalize_deal_name(
                        level=properties['certification_level']['value'],
                        contact=contact,
                        date=timestamp,
                        lang=lang,
                    )

                    payload = {
                        'properties': [
                            {
                                'value': name,
                                'name': 'dealname',
                            },
                        ]
                    }
                    response = requests.put(
                        url=url,
                        data=json.dumps(payload),
                        headers={'Content-Type': 'application/json'}
                    )
                    time.sleep(API_LAPSE)
                    try:
                        assert status.is_success(response.status_code)
                        self.stdout.write(self.style.SUCCESS('Deal successfully updated {}'.format(name)))
                    except AssertionError:
                        logger.info(
                            'ERROR: normalize_hubspot_deals: Could not update Deal {} - Request status code [{}]: {}'.format(  # noqa
                                deal_id, response.status_code, response.content)
                        )
                        return False
        except Exception as exc:
            logger.info('ERROR: normalize_hubspot_deals: Could not update Deal {} - Some error occurred [{}]: {}'.format(  # noqa
                deal_id, type(exc), exc)
            )
            return False
        return True

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('HubSpot Deals normalization started...'))
        # Gets params
        pipeline = kwargs.get('pipeline')[0]

        page_size = 50
        deals_url = API_ROOT_URL + 'deals/v1/deal/paged?'
        params = {
            'hapikey': settings.HAPIKEY,
            'limit': page_size,
        }
        has_more = True

        while has_more:
            query_params = urllib.parse.urlencode(params)
            response = requests.get(url=deals_url + query_params, headers={})
            time.sleep(API_LAPSE)
            try:
                assert status.is_success(response.status_code)
            except AssertionError:
                logger.info('ERROR: normalize_hubspot_deals: Could not get deal list - Request status code [{}]'.format(response.status_code))  # noqa
                return False

            data = response.json()
            has_more = data.get('hasMore', False)
            params['offset'] = data.get('offset')
            for deal in data.get('deals'):
                self.normalize_deal(deal.get('dealId'), pipeline)
