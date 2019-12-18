from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker


class TestResourceURLValidationAPITestCase(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_validate_url_wrong(self):
        # PREPARE DATA
        url_api = reverse('api:resources:validate-url')
        url_validate = faker.url()

        # DO ACTION
        response = self.client.post(url_api, data={'url': url_validate})

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_validate_url_providers(self):
        # PREPARE DATA
        url_api = reverse('api:resources:validate-url')
        urls_validate = [
            "https://vimeo.com/4413241",
            "https://www.youtube.com/watch?v=GPB8ovFD_W4",
            "https://drive.google.com/open?id=1sIBAPpK6S4QerSlS8efIscci5whF6ppX",
            "https://www.dropbox.com/s/o6dnqzyhar647qu/gatos.mp4?dl=0"
        ]

        # DO ACTION
        for url_validate in urls_validate:
            response = self.client.post(url_api, data={'url': url_validate})

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
