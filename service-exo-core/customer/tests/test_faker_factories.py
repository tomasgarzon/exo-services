from django.test import TestCase

from .test_mixins import TestCustomerMixin


class CustomerFakerTest(TestCustomerMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_customer()

    def test_customer_faker(self):
        self.assertIsNotNone(self.customer.name)
        self.assertIsNotNone(self.customer.phone)
