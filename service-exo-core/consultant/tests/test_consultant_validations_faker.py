from django.test import TestCase
from django.test import tag

from ..conf import settings
from ..faker_factories import (
    FakeConsultantFactory,
    FakeConsultantValidationStatusFactory
)


@tag('sequencial')
class ValidationsFakerTest(TestCase):

    def test_consultant_active_faker(self):

        consultant_validation = FakeConsultantValidationStatusFactory()
        consultant = consultant_validation.consultant

        self.assertIsNotNone(consultant_validation.validation)
        self.assertIsNotNone(consultant_validation.consultant)
        self.assertIsNotNone(consultant_validation.status)
        self.assertEqual(consultant.validations.all().count(), 1)

        FakeConsultantValidationStatusFactory(consultant=consultant)

        self.assertEqual(consultant.validations.all().count(), 2)

    def test_consultant_status_and_validations(self):
        """
        This test will check if the consultant status property to validate that
        the Consultant has complete all the requirements works propertly
        """

        consultant = FakeConsultantFactory(
            user__is_active=False,
            status=settings.CONSULTANT_STATUS_CH_DISABLED,
        )
        self.assertFalse(consultant.user.is_active)
        self.assertFalse(consultant.is_active)
        self.assertEqual(consultant.status, settings.CONSULTANT_STATUS_CH_DISABLED)

        # Activate the user and the status of the Consultant have to be Active
        # because at this moment this user have no validations
        consultant.user.is_active = True
        consultant.user.save()

        self.assertTrue(consultant.user.is_active)
        self.assertTrue(consultant.is_active)
        self.assertEqual(consultant.status, settings.CONSULTANT_STATUS_CH_ACTIVE)

        # Add a validation
        consultant_validation = FakeConsultantValidationStatusFactory(
            consultant=consultant,
            status=settings.CONSULTANT_VALIDATION_CH_SENT,
        )
        self.assertFalse(consultant_validation.is_validated)
        self.assertFalse(consultant.is_active)
        consultant_validation.validate()
        consultant.refresh_from_db()

        self.assertTrue(consultant_validation.is_validated)
        self.assertTrue(consultant.is_active)
        self.assertFalse(consultant.is_pending_validation)
        self.assertFalse(consultant.get_pending_validations())

        # Add another invalidated Consultant Validation
        consultant_validation_1 = FakeConsultantValidationStatusFactory(
            consultant=consultant,
            status=settings.CONSULTANT_VALIDATION_CH_PENDING_REVIEW,
        )

        self.assertFalse(consultant_validation_1.is_validated)
        self.assertFalse(consultant.is_active)

        self.assertEqual(consultant.validations.all().count(), 2)

        self.assertTrue(consultant.is_pending_validation)
        self.assertTrue(consultant.get_pending_validations())
