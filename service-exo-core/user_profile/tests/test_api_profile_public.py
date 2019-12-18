from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from rest_framework import status

from exo_role.models import ExORole

from consultant.faker_factories import FakeConsultantFactory
from core.models import Language
from exo_attributes.models import ExOAttribute
from industry.models import Industry
from relation.faker_factories import FakeConsultantProjectRoleFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker


class ProfilePublicAPITest(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()

    def prepare_data(self):
        language_esp = Language.objects.get(name='Spanish')
        language_eng = Language.objects.get(name='English')
        languages = [language_esp, language_eng]

        self.consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__about_me=faker.text(),
            user__bio_me=faker.text(),
            user__short_me=faker.text(),
            user__password='123456',
            languages=languages
        )
        self.user = self.consultant.user
        self.api_url = reverse(
            'api:profile-public:profile-detail',
            kwargs={'slug': self.user.slug},
        )
        self.create_consultant_exo_profile(self.consultant)
        self.create_consultant_project_roles(self.consultant)

    def create_consultant_exo_profile(self, consultant):
        industry = Industry.objects.all().first()
        industry2 = Industry.objects.all().last()
        exo_attr = ExOAttribute.objects.all().first()
        exo_attr2 = ExOAttribute.objects.all().last()
        consultant.industries.create(industry=industry, level=2)
        consultant.industries.create(industry=industry2, level=3)
        consultant.exo_attributes.create(exo_attribute=exo_attr, level=2)
        consultant.exo_attributes.create(exo_attribute=exo_attr2, level=5)
        exo_profile = consultant.exo_profile
        exo_profile.mtp_mastery = 4
        exo_profile.personal_mtp = faker.text()
        exo_profile.save()

    def create_consultant_project_roles(self, consultant):
        sprint = FakeSprintAutomatedFactory.create()
        sprint.set_started(sprint.created_by, timezone.now())
        self.consultant_role = FakeConsultantProjectRoleFactory.create(
            project=sprint.project_ptr,
            consultant=consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
            status=settings.RELATION_ROLE_CH_ACTIVE,
            visible=True,
        )

    def test_profile_public_api(self):
        # PREPARE DATA
        self.prepare_data()

        # DO ACTION
        response = self.client.get(self.api_url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_profile_public_api_response(self):
        # PREPARE DATA
        self.prepare_data()

        # DO ACTION
        response = self.client.get(self.api_url)

        # ASSERTS
        response_data = response.data
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response_data.get('phone'), self.user.phone)
        self.assertEqual(response_data.get('full_name'), self.user.full_name)
        self.assertEqual(response_data.get('about_me'), self.user.about_me)
        self.assertEqual(response_data.get('location'), self.user.location)
        self.assertEqual(response_data.get('timezone'), self.user.timezone)
        self.assertEqual(len(response_data.get('profile_pictures')), 4)

        consultant_response = response_data.get('consultant')
        self.assertEqual(
            consultant_response.get('exo_profile').get('personal_mtp'),
            self.consultant.exo_profile.personal_mtp)
        self.assertEqual(
            consultant_response.get('exo_profile').get('mtp_mastery'),
            self.consultant.exo_profile.mtp_mastery)
        self.assertEqual(len(consultant_response.get('industries')), 2)
        self.assertEqual(len(consultant_response.get('exo_attributes')), 12)

    def test_profile_public_not_visible_project(self):
        # PREPARE DATA
        self.prepare_data()
        self.consultant_role.visible = False
        self.consultant_role.save()

        # DO ACTION
        response = self.client.get(self.api_url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
