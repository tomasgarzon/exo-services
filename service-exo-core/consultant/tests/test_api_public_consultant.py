from django.urls import reverse
from django.test import tag
from django.conf import settings
from django.contrib.auth.models import Permission

from rest_framework import status

from exo_role.models import CertificationRole

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from relation.faker_factories import FakeConsultantRoleFactory

from ..faker_factories import FakeConsultantFactory


@tag('sequencial')
class TestAPIPublicConsultant(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def test_api_autocomplete_ok(self):
        # PREPARE DATA
        FakeConsultantFactory.create_batch(size=2)
        self.create_user()
        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 2)

    def test_private_api_autocomplete_no_page(self):
        # PREPARE DATA
        FakeConsultantFactory.create_batch(size=30)
        self.create_user()
        FakeConsultantFactory.create(user=self.user)
        self.user.user_permissions.add(
            Permission.objects.get(codename=settings.EXO_ACCOUNTS_PERMS_ACCESS_EXQ))

        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')
        data = {'permissions': settings.EXO_ACCOUNTS_PERMS_ACCESS_EXQ}
        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 1)

    def test_filter_by_certifications(self):
        # PREPARE DATA
        FakeConsultantFactory.create_batch(size=2)
        self.create_user()
        consultant = FakeConsultantFactory.create(user=self.user)
        FakeConsultantRoleFactory.create(
            consultant=consultant,
            certification_role=CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER),
        )

        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')
        data = {'certifications': settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER}
        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 1)

    def test_filter_by_certifications_and_search(self):
        # PREPARE DATA
        name1 = 'first name'
        name2 = 'second name'
        name3 = 'therd name'
        self.create_user()
        consultant1 = FakeConsultantFactory.create(
            user__short_name=name1.split()[0],
            user__full_name=name1)
        consultant2 = FakeConsultantFactory.create(
            user__short_name=name2.split()[0],
            user__full_name=name2)
        FakeConsultantFactory.create(
            user__short_name=name3.split()[0],
            user__full_name=name3)
        FakeConsultantRoleFactory.create(
            consultant=consultant1,
            certification_role=CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER),
        )
        FakeConsultantRoleFactory.create(
            consultant=consultant2,
            certification_role=CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER),
        )

        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')
        data = {
            'certifications': settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER,
            'search': 'first'}

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()), 1)
        data = response.json()
        self.assertEqual(data[0]['user_uuid'], consultant1.user.uuid.__str__())

    def test_filter_by_multiple_certifications(self):
        # PREPARE DATA
        certification_role_consultant = CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT)
        certification_role_foundations = CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS)
        certification_role_trainer = CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER)

        FakeConsultantRoleFactory.create(certification_role=certification_role_consultant)
        FakeConsultantRoleFactory.create(certification_role=certification_role_trainer)
        consultant_role = FakeConsultantRoleFactory.create(certification_role=certification_role_foundations)
        FakeConsultantRoleFactory.create(consultant=consultant_role.consultant,
                                         certification_role=certification_role_trainer)
        self.create_user()

        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')
        query_string = {
            'QUERY_STRING': 'certifications={}&certifications={}'.format(
                settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER,
                settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS)}

        # DO ACTION
        response = self.client.get(url, **query_string)

        # ASSERTIONS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 1)

    def test_private_api_autocomplete_page_size(self):
        # PREPARE DATA
        FakeConsultantFactory.create_batch(size=30)
        self.create_user()
        self.client.login(username=self.user.email, password='123456')
        url = reverse('api:consultant:autocomplete-list')

        # DO ACTION
        response = self.client.get(url, data={'page_size': 10})

        # ASSERTIONS
        self.assertEqual(len(response.data), 10)
