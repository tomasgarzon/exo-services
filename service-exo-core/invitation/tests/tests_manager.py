from django.test import TestCase
from django.core.exceptions import ValidationError
from unittest.mock import patch


from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import (
    FakeInvitationFactory,
    FakeInvitationObjectFactory,
    FakeRelatedObjectFactory
)

from .. import models
from ..conf import settings


class InvitationManagerTest(
    SuperUserTestMixin,
    UserTestMixin,
    TestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_user()
        self.user_to = FakeUserFactory(is_active=True)

    def test_expiration_day(self):
        result = models.Invitation.objects._calculate_expiration_day()
        self.assertIsNone(result)
        result = models.Invitation.objects._calculate_expiration_day(days=3)
        self.assertIsNotNone(result)

    @patch.object(models.RelatedObjectFake, 'send_notification')
    def test_create_invitation_role(self, mock_email):
        example = FakeRelatedObjectFactory.create()
        new_user = FakeUserFactory(is_active=True)
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            user=new_user,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=example,
        )
        self.assertTrue(invitation.is_pending)
        self.assertIsNone(invitation.valid_date)
        self.assertIsNotNone(invitation.hash)
        self.assertEqual(invitation.invitation_objects.all().get().content_object, example)
        self.assertFalse(mock_email.called)

    @patch.object(models.RelatedObjectFake, 'send_notification')
    def test_resend_invitation_role(self, mock_email):
        example = FakeRelatedObjectFactory.create()
        new_user = FakeUserFactory(is_active=True)
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            invite_user=self.user,
            user=new_user,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=example,
        )

        self.assertFalse(mock_email.called)
        invitation.resend(self.user)
        self.assertEqual(mock_email.call_count, 1)
        invitation.accept(new_user)
        with self.assertRaises(ValidationError):
            invitation.resend(self.user)

    def test_permission_when_invitation_created(self):
        example = FakeRelatedObjectFactory.create()
        user_from = self.user
        user_to = self.user_to
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            invite_user=self.user,
            user=self.user_to,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=example,
        )

        self.assertTrue(user_from.has_perm(settings.INVITATION_CANCEL, invitation))
        self.assertFalse(user_from.has_perm(settings.INVITATION_ACCEPT, invitation))
        self.assertTrue(user_to.has_perm(settings.INVITATION_CANCEL, invitation))
        self.assertTrue(user_to.has_perm(settings.INVITATION_ACCEPT, invitation))
        self.assertEqual(
            invitation.invitation_objects.all().get().content_object,
            example,
        )

    def test_filter_by_object_role(self):
        """
        This test will check the filter filter_by_object
        """
        example = FakeRelatedObjectFactory.create()
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            invite_user=self.user,
            user=self.user_to,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=example,
        )

        self.assertIsNotNone(models.Invitation.objects.filter_by_object(example))
