from django.test import TestCase

from .mixins import TestPartnerMixin


class PartnerFakerTest(TestPartnerMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_partner()

    def test_customer_faker(self):
        self.assertIsNotNone(self.partner.name)
