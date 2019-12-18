from django.conf import settings
from django.urls import reverse
from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from exo_certification.models import Coupon, ExOCertification
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker

from .test_mixins import ExOCertificationTestMixin


class ExOCertificationCohortAPITestCase(
        ExOCertificationTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        for i in range(4):
            self.create_cohorts()

    def test_cohorts_level_2_guest(self):
        # PREPARE DATA
        url = reverse('api:exo-certification:cohorts')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEquals(len(data), 4)

    def test_cohorts_level_2_guest_with_coupon(self):
        # PREPARE DATA
        certification = ExOCertification.objects.get(
            level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
        )
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=certification,
            max_uses=10,
            uses=0,
            discount=500,
        )
        url = reverse('api:exo-certification:cohorts')

        # DO ACTION
        response = self.client.get(url, data={'coupon': coupon.code})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEquals(len(data), 4)
        self.assertEquals(data[0].get('finalPrice'), 1000)
        self.assertEquals(data[0].get('price'), 1500)
        self.assertEquals(data[0].get('discount'), 500)

    def test_cohorts_level_3(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        url = reverse('api:exo-certification:cohorts')

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url, data={'level': 'L3'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEquals(len(data), 4)
        self.assertEquals(data[0].get('price'), 2500)
        self.assertEquals(data[0].get('finalPrice'), 2500)
        self.assertIsNone(data[0].get('discount'))

    def test_cohorts_level_3_with_coupon(self):
        # PREPARE DATA
        certification = ExOCertification.objects.get(
            level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3
        )
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=certification,
            max_uses=10,
            uses=0,
            discount=500,
        )
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        url = reverse('api:exo-certification:cohorts')

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url, data={'level': 'L3', 'coupon': coupon.code})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEquals(len(data), 4)
        self.assertEquals(data[0].get('price'), 2500)
        self.assertEquals(data[0].get('finalPrice'), 2000)
        self.assertEquals(data[0].get('discount'), 500)
