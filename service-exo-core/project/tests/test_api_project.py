from django.urls import reverse
from django.conf import settings

from rest_framework import status

from utils.faker_factory import faker
from utils.dates import build_datetime, increase_date, decrease_date, string_to_datetime
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils import DjangoRestFrameworkTestCase
from consultant.faker_factories import FakeConsultantFactory
from test_utils import TestInboxMixin


class ProjectAPITestCase(
        SuperUserTestMixin,
        UserTestMixin,
        TestInboxMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_user()
        self.create_superuser()

        FakeConsultantFactory.create(
            user=self.user,
        )
        self.sprint_automated = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_DRAFT,
            start=decrease_date(days=1),
            created_by=self.user)

    def test_get_project_list(self):
        # PREPARE DATA
        self.client.login(
            username=self.super_user.username, password='123456')
        url = reverse('api:project:project-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data),
            1)

    def test_retrieve_project(self):
        # PREPARE DATA
        self.client.login(
            username=self.user.username, password='123456')
        url = reverse('api:project:project-detail', kwargs={'slug': self.sprint_automated.slug})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(data['nextUrl'])
        self.assertIsNotNone(data['profileUrl'])
        self.assertIsNotNone(data['uuid'])

    def test_update_project(self):
        # PREPARE DATA
        self.client.login(
            username=self.user.username, password='123456')
        url = reverse('api:project:project-detail', kwargs={'slug': self.sprint_automated.slug})
        timezone_workshop = 'UTC'
        place_id = 'ChIJgTwKgJcpQg0RaSKMYcHeNsQ'

        # DO ACTION
        data = {
            'name': faker.word(),
            'start': build_datetime(string_to_datetime('2018, 10, 10', custom_timezone='Europe/Madrid')),
            'end': build_datetime(string_to_datetime('2018, 10, 12', custom_timezone='Europe/Madrid')),
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'place_id': place_id,
            'comment': faker.text(),
        }
        response = self.client.put(url, data=data)
        data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.sprint_automated.refresh_from_db()
        self.assertEqual(self.sprint_automated.name, data['name'])
        self.assertEqual(self.sprint_automated.comment, data['comment'])
        self.assertEqual(self.sprint_automated.location, data['location'])
        self.assertEqual(self.sprint_automated.place_id, place_id)
        self.assertEqual(self.sprint_automated.timezone.zone, timezone_workshop)

    def test_project_settings_api(self):
        # PREPARE DATA
        self.client.login(
            username=self.user.username, password='123456')
        url = reverse(
            'api:project:project-settings',
            kwargs={'slug': self.sprint_automated.slug})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.data['launch'].get('fix_password'), None)

        # DO ACTION
        data = response.data
        data['ask_to_ecosystem'] = False
        response = self.client.put(url, data=data, format='json')

        self.assertTrue(status.is_success(response.status_code))
        settings = self.sprint_automated.project_ptr.settings
        self.assertEqual(
            settings.ask_to_ecosystem,
            data['ask_to_ecosystem'])

    def test_project_status_workflow(self):
        # PREPARE DATA
        self.client.login(
            username=self.user.username, password='123456')
        url = reverse(
            'api:project:project-change-status',
            kwargs={'slug': self.sprint_automated.slug})

        # DO ACTION
        statuses = [
            (settings.PROJECT_CH_PROJECT_STATUS_WAITING, 400),
            (settings.PROJECT_CH_PROJECT_STATUS_STARTED, 200),
            (settings.PROJECT_CH_PROJECT_STATUS_FINISHED, 200),
        ]

        for index, data in enumerate(statuses):
            new_status, status_code = data
            date = increase_date(days=index)
            data = {
                'new_status': new_status,
                'date': date.strftime('%m/%d/%Y %H:%M:%S'),
            }
            # DO ACTION
            response = self.client.put(url, data=data, format='json')

            # ASSERTS
            self.assertEqual(response.status_code, status_code)
            self.sprint_automated.refresh_from_db()
            if response.status_code == 200:
                self.assertEqual(self.sprint_automated.status, new_status)
