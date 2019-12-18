from django.test import TestCase

from ..conf import settings
from ..faker_factories import FakeInvitationFactory


class InvitationFakerTest(TestCase):

    def test_invitation_faker(self):
        invitation = FakeInvitationFactory(status=settings.INVITATION_STATUS_CH_ACTIVE)
        self.assertTrue(invitation.user.is_active)
        self.assertTrue(invitation.user.has_usable_password())
        self.assertFalse(invitation.is_pending)
        self.assertFalse(invitation.is_cancelled)
        self.assertTrue(invitation.is_active)

    def test_invitation_pending_faker(self):

        invitation = FakeInvitationFactory(status=settings.INVITATION_STATUS_CH_PENDING)
        self.assertTrue(invitation.user.is_active)
        self.assertTrue(invitation.is_pending)
        self.assertFalse(invitation.is_cancelled)
        self.assertFalse(invitation.is_active)

    def test_invitation_cancelled_faker(self):

        invitation = FakeInvitationFactory(status=settings.INVITATION_STATUS_CH_CANCELLED)
        self.assertTrue(invitation.user.is_active)
        self.assertTrue(invitation.user.has_usable_password())
        self.assertFalse(invitation.is_pending)
        self.assertTrue(invitation.is_cancelled)
        self.assertFalse(invitation.is_active)
