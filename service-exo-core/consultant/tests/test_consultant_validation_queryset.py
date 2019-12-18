from django import test
from django.test import tag

from ..faker_factories import FakeConsultantValidationStatusFactory
from ..models import ConsultantValidationStatus
from ..conf import settings


@tag('sequencial')
class ConsultantQuerySetTest(test.TestCase):

    def setUp(self):
        super().setUp()
        FakeConsultantValidationStatusFactory.create_batch(size=10)

    def test_filter_agreements(self):
        self.assertEqual(
            ConsultantValidationStatus.objects.filter(
                validation__name=settings.CONSULTANT_VALIDATION_AGREEMENT,
            ).count(),
            ConsultantValidationStatus.objects.agreements().count(),
        )
        for _ in ConsultantValidationStatus.objects.agreements():
            self.assertTrue(_.is_agreement)

    def test_filter_applications(self):
        self.assertEqual(
            ConsultantValidationStatus.objects.filter(
                validation__name=settings.CONSULTANT_VALIDATION_APPLICATION,
            ).count(),
            ConsultantValidationStatus.objects.applications().count(),
        )
        for _ in ConsultantValidationStatus.objects.applications():
            self.assertTrue(_.is_application)

    def test_filter_tests(self):
        self.assertEqual(
            ConsultantValidationStatus.objects.filter(
                validation__name=settings.CONSULTANT_VALIDATION_TEST,
            ).count(),
            ConsultantValidationStatus.objects.tests().count(),
        )
        for _ in ConsultantValidationStatus.objects.tests():
            self.assertTrue(_.is_test)
