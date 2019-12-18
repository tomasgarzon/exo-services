from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin


class TestUserLanguageAddress(
    UserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.client.login(username=self.user.email, password='123456')

    def _update_language(self, data):
        api_language_url = reverse(
            'api:profile:change-platform-language',
            kwargs={'pk': self.user.pk},
        )
        response = self.client.put(
            api_language_url,
            data=data,
        )
        self.user.refresh_from_db()

        return response

    def test_change_user_platform_language_should_change_django_language(self):

        data = {'platform_language': settings.LANGUAGE_ES}
        expected_response = data
        response = self._update_language(data)

        self.assertEqual(self.user.platform_language, settings.LANGUAGE_ES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.cookies.get(settings.LANGUAGE_COOKIE_NAME).value,
            settings.LANGUAGE_ES,
        )
        self.assertEqual(response.data, expected_response)

    def test_change_user_platform_language_should_control_undefined_language(self):

        data = {'platform_language': 'XX'}
        response = self._update_language(data)

        self.assertEqual(self.user.platform_language, settings.LANGUAGE_DEFAULT)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
