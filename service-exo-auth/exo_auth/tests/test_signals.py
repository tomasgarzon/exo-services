from django.test import TestCase, override_settings

from mock import patch

from ..faker_factories import FakeUserFactory
from .. import models
from .. import signals_define

from utils.faker_factory import faker


class TestSignals(TestCase):

    @patch.object(signals_define.signal_exo_accounts_user_created, 'send')
    def test_signal_exo_accounts_user_created_send_signal_for_new_users(self,
                                                                        patch_signal):

        # DO ACTIONS
        models.User.objects.get_or_create(email=faker.email())

        # ASSERTS
        self.assertEqual(patch_signal.call_count, 1)

    @patch.object(signals_define.signal_exo_accounts_user_created, 'send')
    def test_signal_exo_accounts_user_created_not_send_signal_for_existing_users(self,
                                                                                 patch_signal):
        # DO ACTIONS
        user, _ = models.User.objects.get_or_create(email=faker.email())

        # DO ACTIONS
        _, created = models.User.objects.get_or_create(email=user.email)

        # ASSERTS
        self.assertFalse(created)
        self.assertEqual(patch_signal.call_count, 1)

    @patch.object(signals_define.signal_exo_user_request_new_password, 'send')
    def test_signal_exo_user_request_new_password_send_signal(self,
                                                              patch_signal):
        # PREPARE DATA
        user = FakeUserFactory.create()

        # DO ACTIONS
        user.send_notification_change_password()

        # ASSERTS
        self.assertEqual(patch_signal.call_count, 1)

    @override_settings(EXO_AUTH_EMAIL_VERIFIACTION_URL_VIEW_NAME=None)
    @patch.object(signals_define.signal_exo_user_new_email_address_unverified,
                  'send')
    def test_exo_user_new_email_address_unverified_raise_error(self,
                                                               patch_signal):
        # PREPARE DATA
        user = FakeUserFactory.create()
        new_email = faker.email()

        # DO ACTION
        user.add_email_address(new_email)

        # ASEERTS
        self.assertEqual(patch_signal.call_count, 1)

    @patch.object(signals_define.signal_exo_user_new_email_address_unverified,
                  'send')
    def test_exo_user_new_email_address_unverified_send_signal(self,
                                                               patch_signal):
        # PREPARE DATA
        user = FakeUserFactory.create()
        new_email = faker.email()

        # DO ACTION
        user.add_email_address(new_email)

        # ASEERTS
        self.assertEqual(patch_signal.call_count, 1)
