from django.urls import reverse
from django.template.defaultfilters import slugify

from rest_framework import status

from utils.faker_factory import faker
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from invitation.models import Invitation
from agreement.models import UserAgreement
from agreement.faker_factories import FakeAgreementFactory
from frontend.helpers import UserRedirectController

from ..conf import settings


class InvitationStatusTest(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def create_validation_agreement(self, validation_type=settings.CONSULTANT_VALIDATION_AGREEMENT):
        consultant = FakeConsultantFactory.create(user=self.user)
        validation_status = consultant.add_validation(self.super_user, validation_type)
        invitation = Invitation.objects.filter_by_object(validation_status).get()
        return consultant, invitation

    def test_accept_agreement_user(self):
        # PREPARE DATA
        consultant, invitation = self.create_validation_agreement()
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:invitation:invitation-accept',
            kwargs={'hash': invitation.hash},
        )

        # DO ACTION
        data = {}
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_active)

    def test_decline_user(self):
        # PREPARE DATA
        consultant, invitation = self.create_validation_agreement()
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:invitation:invitation-decline',
            kwargs={'hash': invitation.hash},
        )

        # DO ACTION
        data = {}
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_cancelled)

    def test_accept_profile_user(self):
        # PREPARE DATA
        consultant, invitation = self.create_validation_agreement(
            settings.CONSULTANT_VALIDATION_BASIC_PROFILE,
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:invitation:invitation-accept',
            kwargs={'hash': invitation.hash},
        )
        image = 'data:image/gif;base64,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'  # NOQA
        location_granada = 'Granada, Spain'
        place_id_granada = 'ChIJfcIyLeb8cQ0Rcg1g0533WJI'
        data = {
            'profilePicture': image,
            'shortName': 'name',
            'fullName': 'name surname',
            'location': location_granada,
            'placeId': place_id_granada,
            'personalMtp': faker.text(),
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_active)
        consultant.refresh_from_db()
        consultant.exo_profile.refresh_from_db()
        user = consultant.user
        user.refresh_from_db()
        self.assertIsNotNone(user.profile_picture)
        self.assertEqual(user.location, data['location'])
        self.assertEqual(user.place_id, data['placeId'])
        self.assertIsNotNone(user.timezone)
        self.assertEqual(
            user.profile_picture_origin,
            settings.EXO_ACCOUNTS_PROFILE_PICTURE_CH_USER)
        self.assertEqual(
            consultant.exo_profile.personal_mtp,
            data['personalMtp'],
        )
        self.assertIsNotNone(consultant.user.slug)
        consultant.user.refresh_from_db()
        self.assertEqual(consultant.user.slug, slugify(data.get('fullName')))

    def test_accept_profile_user_optionals(self):
        # PREPARE DATA
        consultant, invitation = self.create_validation_agreement(
            settings.CONSULTANT_VALIDATION_BASIC_PROFILE,
        )
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        url = reverse(
            'api:invitation:invitation-accept',
            kwargs={'hash': invitation.hash},
        )
        location_granada = 'Granada, Spain'
        place_id_granada = 'ChIJfcIyLeb8cQ0Rcg1g0533WJI'
        data = {
            'profilePicture': '',
            'shortName': faker.first_name(),
            'fullName': faker.name(),
            'location': location_granada,
            'placeId': place_id_granada,
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_active)
        consultant.refresh_from_db()
        user = consultant.user
        user.refresh_from_db()
        self.assertIsNotNone(user.profile_picture)
        self.assertIsNotNone(user.timezone)

    def test_accept_new_agreement_user(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user=self.user)
        previous_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )
        user_agreement = UserAgreement.objects.create(
            agreement=previous_agreement,
            user=consultant.user,
        )
        invitation = Invitation.objects.create_user_agreement(
            self.super_user,
            consultant.user,
            user_agreement,
        )

        url = reverse(
            'api:invitation:invitation-accept',
            kwargs={'hash': invitation.hash},
        )

        # DO ACTION
        self.client.login(
            username=consultant.user.email,
            password='123456',
        )
        data = {}
        response = self.client.post(url, data=data, format='json')

        self.assertTrue(status.is_success(response.status_code))
        invitation.refresh_from_db()
        self.assertTrue(invitation.is_active)
        url, zone = UserRedirectController.redirect_url(consultant.user)
        self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
        self.assertFalse(zone)
