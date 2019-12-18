from django import test
from django.conf import settings
from django.contrib.auth import get_user_model

from mock import patch

from .. import signals_define
from ..test_mixins.faker_factories import FakeUserFactory

from utils.faker_factory import faker


User = get_user_model()


class SocialNetworkTest(test.TestCase):

    def test_add_social_network(self):
        # PREPARE DATA
        user = FakeUserFactory.create()

        # DO ACTIONS
        user.create_social_network(settings.EXO_ACCOUNTS_SOCIAL_SKYPE,
                                   faker.word())

        # ASSERTS
        self.assertEqual(user.social_networks.all().count(), 1)

    def test_update_social_network(self):
        # PREPARE DATA
        user = FakeUserFactory.create()
        user.create_social_network(settings.EXO_ACCOUNTS_SOCIAL_SKYPE,
                                   faker.word())
        skype_name = faker.word()

        # DO ACTIONS
        user.update_social_network(settings.EXO_ACCOUNTS_SOCIAL_SKYPE,
                                   skype_name)

        # ASSERTS
        self.assertTrue(skype_name in
                        user.social_networks.values_list('value', flat=True))

    def test_delete_social_network(self):
        # PREPARE DATA
        user = FakeUserFactory.create()
        user.create_social_network(settings.EXO_ACCOUNTS_SOCIAL_SKYPE,
                                   faker.word())

        # DO ACTIONS
        user.delete_social_network(settings.EXO_ACCOUNTS_SOCIAL_SKYPE)

        # ASSERTS
        self.assertEqual(user.social_networks.all().count(), 0)

    def test_social_network(self):
        # PREPARE DATA
        user = FakeUserFactory.create()
        user.initialize_social_networks()
        skype_name = faker.word()

        # DO ACTIONS
        user.skype = skype_name

        # ASSERTS
        self.assertTrue(skype_name in
                        user.social_networks.values_list('value', flat=True))
        self.assertTrue(user.skype.is_filled)

    def test_user_set_password_send_update_password_signal(self):
        test_cases = [{'data': {'raw_password': None,
                                'random_password': None},
                       'result': False},
                      {'data': {'raw_password': None,
                                'random_password': False},
                       'result': False},
                      {'data': {'raw_password': None,
                                'random_password': True},
                       'result': False},
                      {'data': {'raw_password': faker.word(),
                                'random_password': None},
                       'result': True},
                      {'data': {'raw_password': faker.word(),
                                'random_password': True},
                       'result': True},
                      {'data': {'raw_password': faker.word(),
                                'random_password': False},
                       'result': True}
                      ]

        for test_case in test_cases:
            # PREPARE DATA
            user = FakeUserFactory.create()

            with patch.object(signals_define.signal_password_updated,
                              'send_robust') as patch_signal_password_updated:
                # DO ACTIONS
                raw_password = test_case.get('data').get('raw_password')
                random_password = test_case.get('data').get('random_password')
                user.set_password(raw_password=raw_password,
                                  random_password=random_password)

                # ASSERTS
                self.assertEqual(patch_signal_password_updated.called,
                                 test_case.get('result'))
