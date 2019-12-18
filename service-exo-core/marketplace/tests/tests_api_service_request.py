from django.urls import reverse

from rest_framework import status
from mock import patch

from test_utils import DjangoRestFrameworkTestCase

from ..faker_factories import FakeServiceRequestFactory
from ..models import ServiceRequest


class TestServiceRequestAPITestCase(DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_service_request_creation(self, mock_email_handler):
        # PREPARE DATA
        data = FakeServiceRequestFactory.create()
        url = reverse('api:marketplace:service-request-list')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(ServiceRequest.objects.exists())
        self.assertEqual(ServiceRequest.objects.count(), 1)
        self.assertTrue(mock_email_handler.called)
