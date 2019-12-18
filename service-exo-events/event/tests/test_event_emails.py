import requests_mock

from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from exo_role.models import Category

from utils.test_mixin import UserTestMixin, MockerTestMixin, request_mock_account
from utils.mock_mixins import MagicMockMixin
from utils.faker_factory import faker

from ..models import Event


class EventsEmailsTestCase(UserTestMixin, MockerTestMixin, MagicMockMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user,
            is_consultant=False,
            is_superuser=True)

    @patch('event.tasks.events_tasks.NotifyEventManagerTask.s')
    @patch('event.models.Event.send_workshop_creation_reminder')
    @requests_mock.Mocker()
    def test_workshop_reminder_email(self, mock_notify_manager_task, mock_task, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        data = {
            'title': faker.sentence(),
            'sub_title': faker.sentence(),
            'description': faker.text(),
            'start': timezone.now().date(),
            'end': timezone.now().date(),
            'category': Category.objects.get(code=settings.EXO_ROLE_CATEGORY_WORKSHOP),
            'follow_type': settings.EVENT_CH_FOLLOW_MODE_DEFAULT,
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'url': faker.uri(),
            'languages': [faker.word()],
            'show_price': faker.boolean(),
            'amount': faker.numerify(),
            'currency': settings.EVENT_CH_CURRENCY_EUR,
            'organizers': [
                {
                    'name': faker.name(),
                    'email': faker.email(),
                    'url': faker.uri()
                },
            ],
            'participants': [],
            'user_from': self.super_user,
        }

        # DO ACTION
        Event.objects.create_event(
            force_retrieve_user_data=True,
            **data)

        # ASSERTS
        self.assertTrue(mock_task.called)
