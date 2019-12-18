from django.test import TestCase

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from utils.mail.recipients_handler import recipients_handler

from ..models import ConfigParam


class ConfigNotificationEmailTestCase(TestCase):

    def setUp(self):
        self.user = FakeUserFactory.create()
        self.consultant = FakeConsultantFactory.create()

    def test_config_user_disabled(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_answer')

        recipients = [self.user.email]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients('new_answer', recipients)

        # ASSERTS
        self.assertEqual(new_recipients, [])

        # DO ACTION
        config_param.set_value_for_agent(self.user, True)

        # ASSERTS
        new_recipients = recipients_handler.clear_recipients('new_answer', recipients)
        self.assertEqual(new_recipients, recipients)

    def test_user_disabled_dont_receive_messages(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_answer')
        config_param.set_value_for_agent(self.user, True)
        self.user.is_active = False
        self.user.save()

        recipients = [self.user.email]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients('new_answer', recipients)

        # ASSERTS
        self.assertEqual(new_recipients, [])

    def test_config_consultant_disabled(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_post')
        recipients = [self.consultant.user.email]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients('new_post', recipients)

        # ASSERTS
        self.assertEqual(new_recipients, recipients)

        # DO ACTION
        config_param.set_value_for_agent(self.consultant, False)

        # ASSERTS
        new_recipients = recipients_handler.clear_recipients('new_post', recipients)
        self.assertEqual(new_recipients, [])

    def test_no_config_param(self):
        # PREPARE DATA

        recipients = [self.user.email, faker.email()]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients(None, recipients)

        # ASSERTS
        self.assertEqual(new_recipients, recipients)

    def test_config_two_consultant_disabled(self):
        # PREPARE DATA
        config_param = ConfigParam.objects.get(name='new_post')
        consultant = FakeConsultantFactory.create()
        recipients = [self.consultant.user.email, consultant.user.email]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients('new_post', recipients)

        # ASSERTS
        self.assertEqual(new_recipients, recipients)

        # DO ACTION
        config_param.set_value_for_agent(self.consultant, False)

        # ASSERTS
        new_recipients = recipients_handler.clear_recipients('new_post', recipients)
        self.assertEqual(new_recipients, [consultant.user.email])

    def test_config_param_not_set(self):
        # PREPARE DATA

        recipients = [self.user.email, faker.email()]

        # DO ACTION
        new_recipients = recipients_handler.clear_recipients('new_open_ticket', recipients)

        # ASSERTS
        self.assertEqual(new_recipients, recipients)
