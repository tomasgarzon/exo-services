import json
import logging
import requests

from django.conf import settings
from django.core.management import BaseCommand

from rest_framework import status

from ...helpers.hubspot import normalize_deal_name, datetime_to_hubspot_timestamp
from ...models import CertificationRequest


logger = logging.getLogger('hubspot')


API_ROOT_URL = 'https://api.hubapi.com/'


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-p', '--pk', nargs='+', type=str, help='CertificationRequest PK')

    def get_contact(self, certification):
        if certification.user:
            contact = '{} {}'.format(
                certification.user.full_name,
                certification.user.email,
            )
        else:
            contact = '{} {}'.format(
                certification.requester_name,
                certification.requester_email,
            )
        return contact

    def request_hubspot(self, deal_id, payload):
        url = '{}deals/v1/deal/{}?hapikey={}'.format(
            API_ROOT_URL,
            deal_id,
            settings.HAPIKEY,
        )

        response = requests.put(
            url=url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        try:
            assert status.is_success(response.status_code)
            message = 'Deal successfully updated {} [{}]'.format(
                response.json()['properties']['dealname']['value'], deal_id)
            logger.info('SUCCESS: {}'.format(message))
            self.stdout.write(self.style.SUCCESS(message))
        except AssertionError:
            logger.info(
                'ERROR: synchronize_certification_deal: Could not update Deal {} - Request status code [{}]: {}'.format(  # noqa
                    deal_id, response.status_code, response.content)
            )

    def handle(self, *args, **kwargs):
        pk = kwargs.get('pk')[0]

        try:
            date = None
            lang = None

            certification_request = CertificationRequest.objects.get(pk=pk)
            assert certification_request.hubspot_deal

            if certification_request.cohort:
                date = certification_request.cohort.date
                lang = certification_request.cohort.language

            name = normalize_deal_name(
                level=certification_request.certification.level,
                contact=self.get_contact(certification_request),
                date=date,
                lang=lang,
            )

            properties = [
                {
                    'value': name,
                    'name': 'dealname',
                },
                {
                    'value': settings.EXO_CERTIFICATION_HS_LEVEL_DEAL_MAPPING.get(
                        certification_request.certification.level
                    ),
                    'name': 'certification_level',
                },
            ]

            if lang:
                properties.append({'value': lang, 'name': 'certification_language'})

            if date:
                properties.append({
                    'value': datetime_to_hubspot_timestamp(date),
                    'name': 'certification_program',
                })

            if certification_request.price:
                properties.append({'value': certification_request.price, 'name': 'amount'})

            self.request_hubspot(
                deal_id=certification_request.hubspot_deal,
                payload={'properties': properties},
            )

        except AssertionError:
            logger.info('ERROR: synchronize_certification_deal: CertificationRequest {} Has no associated deal'.format(pk))  # noqa
        except CertificationRequest.DoesNotExist:
            logger.info('ERROR: synchronize_certification_deal: There\'s no CertificationRequest with pk={}'.format(pk))  # noqa
