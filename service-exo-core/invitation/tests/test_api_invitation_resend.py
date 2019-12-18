from django.urls import reverse

from rest_framework import status
from mock import patch

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..faker_factories import (
    FakeInvitationFactory,
    FakeInvitationObjectFactory,
    FakeRelatedObjectFactory
)
from ..conf import settings
from .. import models


class InvitationResendTest(
    SuperUserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_resend_no_user(self):
        invitation = FakeInvitationFactory.create(type=settings.INVITATION_TYPE_SIMPLE_SIGNUP)
        url = reverse(
            'api:invitation:resend-email',
            kwargs={'pk': invitation.pk},
        )
        response = self.client.put(url, data={}, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    @patch.object(models.RelatedObjectFake, 'send_notification')
    @patch.object(models.RelatedObjectFake, 'mark_as_pending')
    def test_resend_user(self, mock_mark, mock_send):
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=FakeRelatedObjectFactory.create(),
        )

        user = invitation.invite_user
        user.set_password('123456')
        user.save()
        self.client.login(username=user.email, password='123456')
        url = reverse(
            'api:invitation:resend-email',
            kwargs={'pk': invitation.pk},
        )
        response = self.client.put(url, data={}, format='json')
        self.assertTrue(mock_send.called)
        self.assertTrue(status.is_success(response.status_code))

    @patch.object(models.RelatedObjectFake, 'send_notification')
    def test_resend_user_email_ok(self, mock_send):
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=FakeRelatedObjectFactory.create(),
        )
        new_user = invitation.user
        user = invitation.invite_user
        user.set_password('123456')
        user.save()
        self.client.login(username=user.email, password='123456')
        url = reverse('api:invitation:resend-user', kwargs={'pk': invitation.pk})
        # change email
        new_email = faker.email()
        data = {'email': new_email}
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        new_user.refresh_from_db()
        self.assertEqual(new_user.email, new_email)
        self.assertTrue(mock_send.called)
        mock_send.assert_called_once_with(invitation)
        # resend without changing email
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(mock_send.call_count, 2)
        self.assertTrue(status.is_success(response.status_code))
        new_user.refresh_from_db()
        self.assertEqual(new_user.email, new_email)

    def test_resend_user_email_duplicated(self):
        invitation = FakeInvitationFactory.create(
            status=settings.INVITATION_STATUS_CH_PENDING,
            valid_date=None,
        )
        FakeInvitationObjectFactory.create(
            invitation=invitation,
            content_object=FakeRelatedObjectFactory.create(),
        )
        new_user = invitation.user
        user = invitation.invite_user
        user.set_password('123456')
        user.save()
        self.client.login(username=user.email, password='123456')
        url = reverse('api:invitation:resend-user', kwargs={'pk': invitation.pk})
        # change email
        new_email = user.email
        data = {'email': new_email}
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
        new_user.refresh_from_db()
        self.assertNotEqual(new_user.email, new_email)
