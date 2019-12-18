from django.urls import reverse
from django.test import tag

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from core.models import Language


@tag('sequencial')
class SummaryAPITests(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_change_summary(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__bio_me=None,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:summary',
            kwargs={'pk': consultant.user.pk},
        )
        location_granada = 'Granada, Spain'
        place_id_granada = 'ChIJfcIyLeb8cQ0Rcg1g0533WJI'
        timezone_granada = 'Europe/Madrid'
        data = {
            'short_name': faker.first_name(),
            'full_name': faker.name(),
            'location': location_granada,
            'place_id': place_id_granada,
            'timezone': timezone_granada,
            'languages': [lang.pk for lang in Language.objects.all()[:2]],
        }

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        consultant.user.refresh_from_db()
        consultant.refresh_from_db()
        user = consultant.user
        self.assertEqual(user.short_name, data['short_name'])
        self.assertEqual(consultant.languages.count(), 2)
        self.assertEqual(user.location, location_granada)
        self.assertEqual(user.place_id, place_id_granada)
        self.assertEqual(user.timezone.zone, timezone_granada)

    def test_change_summary_not_required(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__bio_me=None,
            user__password='123456',
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:profile:summary',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'short_name': faker.first_name(),
            'full_name': '',
            'timezone': 'Canada/Eastern',
        }

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        consultant.user.refresh_from_db()
        consultant.refresh_from_db()
        user = consultant.user
        self.assertEqual(user.short_name, data['short_name'])
        self.assertEqual(consultant.languages.count(), 0)
        self.assertEqual(user.timezone.zone, 'Canada/Eastern')
