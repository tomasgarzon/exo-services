from django.test import TestCase
from django.contrib.auth import get_user_model

from exo_messages.conf import settings
from exo_messages.models import Message
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.faker_factory import faker

User = get_user_model()


class InternalMessageTest(TestCase):

    def test_change_password_pending(self):
        # PREPARE DATA
        user = FakeUserFactory.create(password='123456')
        Message.objects.create_message(
            user=user,
            code=settings.EXO_MESSAGES_CH_CODE_PENDING_PASSWORD,
            level=settings.EXO_MESSAGES_CH_ERROR
        )
        # PRE ASSERTIONS
        self.assertEqual(Message.objects.filter_by_user(user).count(), 1)

        # DO ACTION
        user.set_password(faker.name())

        # ASSERTS
        self.assertEqual(Message.objects.filter_by_user(user).count(), 0)
