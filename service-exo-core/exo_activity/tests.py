from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin


class ExOActivityAPITestCase(UserTestMixin, DjangoRestFrameworkTestCase):

    def test_exo_activity_api(self):
        # PREPARE DATA
        self.create_user()
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        url = reverse('api:exo-activity:activity-list')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(len(response.json()), 10)
