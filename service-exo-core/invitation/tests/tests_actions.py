from django.test import TestCase

from test_utils.test_case_mixins import UserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..conf import settings

from ..faker_factories import (
    FakeInvitationFactory,
    FakeInvitationObjectFactory,
    FakeRelatedObjectFactory
)


class InvitationActionTest(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.user_to = FakeUserFactory.create(is_active=True)

    def test_perms_invitation(self):
        invitation = FakeInvitationFactory.create(
            invite_user=self.user,
            user=self.user_to,
            status=settings.INVITATION_STATUS_CH_PENDING,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=FakeRelatedObjectFactory.create(),
        )

        self.assertTrue(self.user.has_perm(settings.INVITATION_CANCEL, invitation))
        self.assertFalse(self.user.has_perm(settings.INVITATION_ACCEPT, invitation))
        self.assertTrue(self.user_to.has_perm(settings.INVITATION_CANCEL, invitation))
        self.assertTrue(self.user_to.has_perm(settings.INVITATION_ACCEPT, invitation))
        self.assertFalse(invitation.can_be_accepted(self.user))
        self.assertTrue(invitation.can_be_accepted(self.user_to))
