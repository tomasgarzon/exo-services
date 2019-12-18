from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin


class TestUserLanguageAddress(
    UserTestMixin,
    DjangoRestFrameworkTestCase
):

    def test_get_default_user_platform_language(self):
        self.create_user()
        self.client.login(username=self.user.email, password='123456')

        response = self.client.get(reverse('api:accounts:me'))
        retrieved_language = response.data[0].get('platform_language')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            retrieved_language,
            settings.LANGUAGE_DEFAULT,
        )
