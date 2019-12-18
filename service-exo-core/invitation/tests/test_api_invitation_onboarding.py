from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from consultant.faker_factories import FakeConsultantFactory

from ..conf import settings
from .. import models


class InvitationOnboardingAPITest(
    SuperUserTestMixin,
    UserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_user()

    def create_invitation(self, validation_type=settings.CONSULTANT_VALIDATION_AGREEMENT):
        consultant = FakeConsultantFactory.create(user=self.user)
        validation_status = consultant.add_validation(self.super_user, validation_type)
        invitation = models.Invitation.objects.filter_by_object(validation_status).get()
        return consultant, invitation

    def test_retrieve_signup(self):
        # PREPARE DATA
        consultant, invitation = self.create_invitation(settings.CONSULTANT_VALIDATION_USER)
        url = reverse('api:invitation:boarding-detail', kwargs={'hash': invitation.hash})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = eval(response.content)
        self.assertEqual(
            data.get('extraData'),
            {'email': consultant.user.email})

    def test_retrieve_agreeent(self):
        # PREPARE DATA
        consultant, invitation = self.create_invitation()
        url = reverse('api:invitation:boarding-detail', kwargs={'hash': invitation.hash})
        fields_expected = ['name', 'file', 'text']

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        for field in fields_expected:
            self.assertTrue(
                field in data.get('extraData').keys(),
                '{} not included'.format(field)
            )

    def test_retrieve_profile(self):
        # PREPARE DATA
        consultant, invitation = self.create_invitation(settings.CONSULTANT_VALIDATION_BASIC_PROFILE)
        url = reverse('api:invitation:boarding-detail', kwargs={'hash': invitation.hash})
        fields_expected = [
            'profilePicture', 'profilePictureOrigin', 'fullName',
            'shortName', 'location', 'placeId', 'personalMtp']

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        for field in fields_expected:
            self.assertTrue(
                field in data.get('extraData').keys(),
                '{} not included'.format(field)
            )
