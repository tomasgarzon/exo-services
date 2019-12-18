import random

from django.conf import settings

from unittest.mock import patch
from model_mommy import mommy

from exo_role.models import Category, ExORole

from utils.faker_factory import faker

from ..models import Event, Participant


class TestEventMixin:

    def setUp(self):
        super().setUp()
        self.notify_event_patcher = patch('event.tasks.events_tasks.NotifyEventManagerTask.s')
        self.notify_event_patcher.start()

    def create_mommy_event(self, user, category_code=None, *args, **kwargs):
        event_category = Category.objects.get(code=category_code or settings.EXO_ROLE_CATEGORY_OTHER)
        return mommy.make(
            Event,
            created_by=user,
            category=event_category,
            languages=kwargs.pop('languages', [faker.word(), ]),
            **kwargs,
        )

    def create_mommy_participant(self, event, user, user_role=None, *args, **kwargs):
        if not user_role:
            event_role_codes = settings.EVENT_PARTICIPANT_ROLE_CHOICES.get(event.category.code)
            random_participant_role_code = event_role_codes[random.randint(0, len(event_role_codes) - 1)][0]

        participant_role_code = user_role or random_participant_role_code
        participant_role = ExORole.objects.get(code=participant_role_code)

        return mommy.make(
            Participant,
            event=event,
            user=user,
            exo_role=participant_role,
            **kwargs,
        )

    def tearDown(self):
        super().tearDown()
        self.notify_event_patcher.stop()
