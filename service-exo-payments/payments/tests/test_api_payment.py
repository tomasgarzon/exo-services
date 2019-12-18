from django.urls import reverse
from django.conf import settings
from django.test import override_settings
from django.utils import timezone

import base64
import hmac
import hashlib
import requests_mock

from decimal import Decimal, ROUND_DOWN

from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from auth_uuid.jwt_helpers import _build_jwt

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Payment
from .. import models


@override_settings(POPULATOR_MODE=True)
class PaymentAPITest(
        UserTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()

    def get_payment_data(self):
        return {
            'amount': '2000',
            'currency': settings.PAYMENTS_CH_USD,
            'concept': faker.sentence(),
            'detail': faker.sentence(),
            'email': faker.email(),
            'full_name': faker.name(),
            'tax_id': faker.word(),
            'address': faker.address(),
            'country': faker.country(),
            'country_code': 'ES',
            'company_name': faker.word(),
            'send_by_email': False,
            'send_invoice': True,
            '_type': settings.PAYMENTS_TYPE_CERTIFICATION,
            'notes': faker.sentence(),
        }

    @requests_mock.Mocker()
    def test_create_request_error(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        token = _build_jwt(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        data = {
            'concept': faker.sentence(),
            'amount': Decimal(10.2).quantize(Decimal('.01'), rounding=ROUND_DOWN),
            'currency': settings.PAYMENTS_CH_USD,
            'email': faker.email(),
            'full_name': faker.name(),
            'url': faker.uri(),
            'token': 'aaaa',
        }
        url = reverse('api:do-request')

        # DO ACTION
        response = self.client.post(url, json=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_create_request_success(self, mock_request, mock_email):
        # PREPARE DATA
        self.init_mock(mock_request)
        token = _build_jwt(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        data = {
            'concept': faker.sentence(),
            'amount': Decimal(10.2).quantize(Decimal('.01'), rounding=ROUND_DOWN),
            'currency': settings.PAYMENTS_CH_USD,
            'email': faker.email(),
            'full_name': faker.name(),
        }
        secret_key = settings.PAYMENT_SECRET_KEY
        dig = hmac.new(
            secret_key.encode(),
            msg=str(data).encode(),
            digestmod=hashlib.sha256).digest()
        data['token'] = base64.b64encode(dig).decode()
        data['url'] = faker.uri()
        url = reverse('api:do-request')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        self.assertEqual(models.Payment.objects.count(), 1)
        payment = models.Payment.objects.first()
        self.assertEqual(
            payment.url_notification, data['url'])
        self.assertEqual(
            payment.created_by, self.user)

    def test_api_create_payment_from_service_needs_authentication(self):
        # PREPARE DATA
        url = reverse('api:create-payment')

        # DO ACTION
        response = self.client.post(url, data={})

        # ASSERTS
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_api_create_payment_from_service(self, mock_request, mock_email):
        # PREPARE DATA
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        data = self.get_payment_data()
        data['type_payment'] = settings.PAYMENTS_TYPE_CERTIFICATION
        data['notify_webhook'] = faker.uri()
        data['amount'] = '2000'

        url = reverse('api:create-payment')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        payment = models.Payment.objects.first()
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(mock_email.called)

        self.assertEqual(models.Payment.objects.count(), 1)

        self.assertEqual(payment.amount_normalized, 200000)
        self.assertIsNotNone(payment.url_notification)
        self.assertEqual(payment.absolute_url, response.json()['nextUrl'])

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_calculate_amount(self, mock_request, mock_email):
        # PREPARE DATA
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)

        data = self.get_payment_data()

        # DO ACTION
        payment = models.Payment.objects.create(**data)
        payment.set_invoice_id()
        payment.calculate_amount()

        # ASSERTS
        self.assertFalse(payment.send_by_email)
        self.assertIsNone(payment.attached_filename)
        self.assertEqual(payment.currency, data.get('currency'))
        self.assertIsNotNone(payment.uuid)
        self.assertEqual(payment._type, settings.PAYMENTS_TYPE_CERTIFICATION)
        self.assertEqual(
            payment.invoice_id,
            '{}{}0001'.format(
                settings.PAYMENTS_TYPE_CERTIFICATION, timezone.now().year.__str__()[2:]))
        self.assertEqual(payment.vat, settings.PAYMENTS_VAT_DEFAULT)
        self.assertEqual(
            payment.amount_eur,
            round(float(data['amount']) * rate_response['rates']['EUR'] * 0.99, 2))
        self.assertEqual(
            payment.amount_vat,
            round(payment.amount_eur * 0.21, 2))
        self.assertTrue(payment.has_VAT)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_calculate_amount_no_vat(self, mock_request, mock_email):
        # PREPARE DATA
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)

        data = self.get_payment_data()
        data['country_code'] = 'FR'

        # DO ACTION
        payment = models.Payment.objects.create(**data)
        payment.calculate_amount()

        # ASSERTS
        self.assertEqual(payment.vat, 0)
        self.assertEqual(
            payment.amount_eur,
            round(float(data['amount']) * rate_response['rates']['EUR'] * 0.99, 2),
        )
        self.assertEqual(payment.amount_vat, 0)
        self.assertFalse(payment.has_VAT)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_process_payment(self, mock_request, mock_email):
        # PREPARE DATA
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)

        fake_url = faker.uri()
        mock_webhook = mock_request.register_uri('PUT', fake_url, json={})
        data = self.get_payment_data()
        data['url_notification'] = fake_url

        payment = models.Payment.objects.create(**data)
        payment.calculate_amount()

        # DO ACTION
        payment.status = settings.PAYMENTS_CH_PAID
        payment.save(update_fields=['status'])

        # ASSERTS
        self.assertTrue(mock_email.called)
        self.assertTrue(mock_webhook.called)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_api_update_payment_from_service(
            self, mock_request, mock_email):
        # PREPARE DATA
        old_intent_id = faker.word()
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}
        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        new_amount = 500
        new_country = 'NO'
        new_concept = 'edited'
        payment_data = self.get_payment_data()
        payment = models.Payment.objects.create(**payment_data)
        payment.intent_id = old_intent_id
        payment.save()
        payment_data['amount'] = new_amount
        payment_data['country_code'] = new_country
        payment_data['concept'] = new_concept

        url = reverse('api:update-payment', kwargs={'uuid': str(payment.uuid)})

        # DO ACTION
        response = self.client.put(url, data=payment_data)
        payment.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(new_concept, payment.concept)
        self.assertEqual(new_country, payment.country_code)
        self.assertEqual(new_amount, payment.amount)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_create_payment_with_api_do_not_generate_invoice(self, mock_request, mock_email):
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        data = self.get_payment_data()
        data['type_payment'] = settings.PAYMENTS_TYPE_CERTIFICATION
        data['notify_webhook'] = faker.uri()
        data['amount'] = '2000'

        url = reverse('api:create-payment')

        # DO ACTION
        self.client.post(url, data=data)

        # ASSERTIONS
        payment = Payment.objects.first()

        self.assertIsNone(payment.invoice_id)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_invoice_id_generated_after_payment_success(self, mock_request, mock_email):
        # PREPARE DATA
        rate_response = {
            'base': 'USD',
            'rates': {'EUR': 0.9},
            'date': '2019-08-06'}

        mock_request.register_uri(
            'GET',
            'https://api.ratesapi.io/api/latest?base=USD&symbols=EUR&rtype=fpy',
            json=rate_response)

        fake_url = faker.uri()
        mock_request.register_uri('PUT', fake_url, json={})
        data = self.get_payment_data()
        data['url_notification'] = fake_url

        payment = models.Payment.objects.create(**data)
        payment.calculate_amount()

        # DO ACTION
        payment.payment_intent_success(faker.word())

        # ASSERTS
        self.assertIsNotNone(payment.invoice_id)
        self.assertEqual(payment.status, settings.PAYMENTS_CH_PAID)
