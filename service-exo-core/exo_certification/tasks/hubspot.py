import json
import logging

import requests
from celery import Task
from django.conf import settings
from rest_framework import status

from consultant.hubspot.contact import HubSpotException, Contact

from ..helpers.hubspot import datetime_to_hubspot_timestamp, get_entry_point_by_level
from ..models import CertificationRequest

logger = logging.getLogger('hubspot')

DEAL_URL = 'https://api.hubapi.com/deals/v1/deal/{}?hapikey={}'
HEADERS = {
    'Content-Type': 'application/json',
}

RETRY_CODES = [
    status.HTTP_429_TOO_MANY_REQUESTS,
    status.HTTP_502_BAD_GATEWAY,
]


class HubspotCertificationDealSyncMixin:

    def set_cancelled_pipeline(self, certification_pk, deal_pk=None):
        if not deal_pk:
            logger.info(
                'ERROR: Cannot DELETE deal. Certification Deal [{}] does not exist for Certification Request {}'.format(  # noqa
                    deal_pk, certification_pk)
            )
            return False

        url = DEAL_URL.format(deal_pk, settings.HAPIKEY)

        response = requests.delete(url, headers=HEADERS)
        try:
            assert status.is_success(response.status_code)
            logger.info('SUCCESS: Certification Request [{}] succesfully deleted'.format(certification_pk))
        except AssertionError:
            logger.info(
                'ERROR: Exception deleting Certification Deal [{}] for certification: {} - Request status code [{}]'.format(  # noqa
                    deal_pk, certification_pk, response.status_code)
            )


class HubspotCertificationDealDeleteTask(
        HubspotCertificationDealSyncMixin,
        Task):
    name = 'HubspotCertificationDealDeleteTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        certification_pk = kwargs.get('certification_pk')
        deal_pk = kwargs.get('deal_pk')
        self.set_cancelled_pipeline(certification_pk, deal_pk)


class HubspotCertificationDealSyncTask(
        HubspotCertificationDealSyncMixin,
        Task):
    name = 'HubspotCertificationDealSyncTask'
    ignore_results = True

    def set_draft_pipeline(self, certification_request, email):
        if certification_request.hubspot_deal:
            logger.info(
                'INFO: Certification Deal [{}] already registered on HubSpot'.format(
                    certification_request.hubspot_deal)
            )
            return True

        try:
            contact = Contact.get_contact(email)
        except HubSpotException:
            contact = Contact(
                full_name=certification_request.requester_name,
                email=email,
                onboarding_entry_point=get_entry_point_by_level(
                    certification_request.certification.level
                ),
                interested_joining_the_community='',
            )
            contact.update_or_create_contact()

        url = DEAL_URL.format('', settings.HAPIKEY)
        payload = {
            'associations': {
                'associatedCompanyIds': [],
                'associatedVids': [contact.vid],
            },
            'properties': [
                {
                    'value': '{} - {} {}'.format(
                        certification_request.certification.level,
                        certification_request.requester_name,
                        email
                    ),
                    'name': 'dealname',
                },
                {
                    'value': settings.EXO_CERTIFICATION_HS_LEVEL_DEAL_MAPPING.get(
                        certification_request.certification.level
                    ),
                    'name': 'certification_level',
                },
                {
                    'value': '{}{}'.format(
                        settings.HS_PIPELINE_PREFIX,
                        settings.EXO_CERTIFICATION_HS_PIPELINE_ID,
                    ),
                    'name': 'pipeline',
                },
                {
                    'value': settings.EXO_CERTIFICATION_HS_STAGE_INTERESTED,
                    'name': 'dealstage',
                }
            ]
        }

        response = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        try:
            assert status.is_success(response.status_code)
            data = response.json()
            certification_request.hubspot_deal = data.get('dealId', None)
            certification_request.save()
            logger.info('SUCCESS: Certification Request [{}] {} succesfully created'.format(
                certification_request.pk, certification_request)
            )
        except AssertionError:
            logger.info(
                'ERROR: Exception creating Certification Deal [{}] to contact: {} - {}'.format(  # noqa
                    certification_request, email, response.json())
            )
            if response.status_code in RETRY_CODES:
                self.retry(countdown=60, max_retries=3)

    def set_pending_pipeline(self, certification_request):
        if not certification_request.hubspot_deal:
            logger.info(
                'ERROR: Cannot set deal as pending. Certification Deal [{}] does not exist for Certification Request {}'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk)
            )
            return False

        url = DEAL_URL.format(certification_request.hubspot_deal, settings.HAPIKEY)

        try:
            full_name = certification_request.user.full_name
        except AttributeError:
            full_name = certification_request.requester_name

        payload = {
            'properties': [
                {
                    'value': '{} ({} {}) {} {}'.format(
                        certification_request.certification.level,
                        certification_request.cohort.date.strftime('%h'),
                        certification_request.cohort.language,
                        full_name,
                        certification_request.user.email,
                    ),
                    'name': 'dealname',
                },
                {
                    'value': settings.EXO_CERTIFICATION_HS_STAGE_PROCEED_PAYMENT,
                    'name': 'dealstage',
                },
                {
                    'value': certification_request.price,
                    'name': 'amount',
                },
                {
                    'value': datetime_to_hubspot_timestamp(certification_request.cohort.date),
                    'name': 'certification_program',
                },
                {
                    'value': certification_request.cohort.language,
                    'name': 'certification_language',
                },
            ]
        }

        response = requests.put(url, headers=HEADERS, data=json.dumps(payload))
        try:
            assert status.is_success(response.status_code)
            logger.info('SUCCESS: Certification Request [{}] {} succesfully updated'.format(
                certification_request.pk, certification_request)
            )
        except AssertionError:
            logger.info(
                'ERROR: Exception updating Certification Deal [{}] for certification: {} - Request status code [{}]'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk, response.status_code)
            )
            if response.status_code in RETRY_CODES:
                self.retry(countdown=60, max_retries=3)

    def set_paid_pipeline(self, certification_request):
        if not certification_request.hubspot_deal:
            logger.info(
                'ERROR: Cannot set deal as paid. Certification Deal [{}] does not exist for Certification Request {}'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk)
            )
            return False

        url = DEAL_URL.format(certification_request.hubspot_deal, settings.HAPIKEY)

        payload = {
            'properties': [
                {
                    'value': settings.EXO_CERTIFICATION_HS_STAGE_PAYMENT_RECEIVED,
                    'name': 'dealstage',
                },
                {
                    'value': '{}{}'.format(
                        settings.HS_PIPELINE_PREFIX,
                        settings.EXO_CERTIFICATION_HS_PIPELINE_ID,
                    ),
                    'name': 'pipeline',
                },
            ]
        }

        response = requests.put(url, headers=HEADERS, data=json.dumps(payload))
        try:
            assert status.is_success(response.status_code)
            logger.info('SUCCESS: Certification Request [{}] {} succesfully updated'.format(
                certification_request.pk, certification_request)
            )
        except AssertionError:
            logger.info(
                'ERROR: Exception updating Certification Deal [{}] for certification: {} - Request status code [{}]'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk, response.status_code)
            )
            if response.status_code in RETRY_CODES:
                self.retry(countdown=60, max_retries=3)

    def set_certification_issued_pipeline(self, certification_request):
        if not certification_request.hubspot_deal:
            logger.info(
                'ERROR: Cannot set deal as certified. Certification Deal [{}] does not exist for Certification Request {}'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk)
            )
            return False

        url = DEAL_URL.format(certification_request.hubspot_deal, settings.HAPIKEY)

        payload = {
            'properties': [
                {
                    'value': settings.EXO_CERTIFICATION_HS_STAGE_CERTIFICATION_ISSUED,
                    'name': 'dealstage',
                },
            ]
        }

        response = requests.put(url, headers=HEADERS, data=json.dumps(payload))
        try:
            assert status.is_success(response.status_code)
            logger.info('SUCCESS: Certification Request [{}] {} succesfully updated'.format(
                certification_request.pk, certification_request)
            )
        except AssertionError:
            logger.info(
                'ERROR: Exception settting as certified Certification Deal [{}] for certification: {} - Request status code [{}]'.format(  # noqa
                    certification_request.hubspot_deal, certification_request.pk, response.status_code)
            )
            if response.status_code in RETRY_CODES:
                self.retry(countdown=60, max_retries=3)

    def run(self, *args, **kwargs):
        certification_request = CertificationRequest.objects.get(pk=kwargs.get('pk'))
        if certification_request.user:
            email = certification_request.user.email
        else:
            email = certification_request.requester_email

        if certification_request.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DRAFT:
            self.set_draft_pipeline(certification_request, email)
        elif certification_request.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING:
            self.set_pending_pipeline(certification_request)
        elif certification_request.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED:
            self.set_paid_pipeline(certification_request)
        elif certification_request.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_CANCELLED:
            self.set_cancelled_pipeline(certification_request.pk, certification_request.hubspot_deal)
        elif certification_request.status == settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_FINISHED:
            self.set_certification_issued_pipeline(certification_request)
