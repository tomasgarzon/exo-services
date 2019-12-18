from django.test import TestCase
from django.test import tag

from exo_accounts.test_mixins.faker_factories import FakeSocialNetworkFactory

from ..faker_factories import FakeConsultantFactory


@tag('sequencial')
class ConsultantFakerTest(TestCase):

    def test_consultant_faker(self):
        consultant = FakeConsultantFactory()
        self.assertTrue(consultant.user.is_active)
        self.assertTrue(consultant.user.has_usable_password())
        self.assertFalse(consultant.user.is_admin)

    def test_consultant_active_faker(self):

        consultant = FakeConsultantFactory(user__is_active=True)
        self.assertTrue(consultant.user.is_active)
        self.assertFalse(consultant.user.is_admin)

    def test_create_social_network(self):
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        social = FakeSocialNetworkFactory.create(user=user)
        self.assertEqual(social.user, user)
        self.assertIsNotNone(social.network_type)
        self.assertIsNotNone(social.value)
