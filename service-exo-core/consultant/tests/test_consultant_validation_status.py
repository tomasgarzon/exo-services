from django.test import TestCase
from django.db.utils import IntegrityError
from django.test import tag

from ..models import ConsultantValidation, ConsultantValidationStatus

from ..faker_factories import (
    FakeConsultantFactory,
    FakeConsultantValidationStatusFactory
)


@tag('sequencial')
class ValidationsFakerTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_unique_together(self):
        """
            Check the UniqueTogether restriction for Consultant/Validation
        """
        validation = ConsultantValidation.objects.all()
        self.assertIsNotNone(validation)

        validation1 = validation[0]
        consultant = FakeConsultantFactory()
        consultant_validation = FakeConsultantValidationStatusFactory(
            consultant=consultant,
            validation=validation1,
        )

        self.assertIsNotNone(consultant_validation)

        with self.assertRaises(IntegrityError):
            validation2 = ConsultantValidationStatus(
                user_from=consultant_validation.user_from,
                validation=validation1,
                consultant=consultant,
            )
            validation2.save()
