from datetime import datetime

from certification.models import CertificationGroup
from django.contrib.auth.models import Group

from exo_certification.management.commands import create_certificates
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from utils.faker_factory import faker


class UserTestMixin:
    def do_login(self, user, password='123456'):
        self.client.login(
            username=user.username,
            password=password,
        )

    def setUp(self):
        super().setUp()

    def create_user(self, password=None):
        """
        Creates an user and add to the class context
        """
        password = password or '123456'
        self.user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password,
        )

    def create_inactive_user(self):
        self.user = FakeUserFactory.create(is_superuser=False)

    def create_new_user(self, password=None, group_name=None):
        """
        Creates a new User for test that need it
        """
        password = password or '123456'
        user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password,
        )

        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.user_set.add(user)
        return user


class SuperUserTestMixin:

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def create_superuser(self, password=None):
        password = password or '123456'
        self.super_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True,
            is_staff=True,
            password=password,
        )


class CertificationTestMixin:

    def certificate_consultant(self, email, _type, user_from):
        certificate = create_certificates.Command()
        course_name = faker.word()
        consultant_role_group = certificate.create_consultant_role_group(
            user_from=user_from,
            name=course_name,
            description=' '.join(faker.words()),
            issued_on=datetime.now(),
            _type=_type,
        )
        certificate.create_consultant_roles(
            emails=[email],
            role_code=certificate.get_role_code(_type),
            consultant_role_group=consultant_role_group,
        )
        data = {
            'name': consultant_role_group.name,
            'description': consultant_role_group.description,
            'content_object': consultant_role_group,
            '_type': consultant_role_group._type,
            'created_by': user_from,
            'instructor_name': user_from.get_full_name(),
        }
        data['issued_on'] = consultant_role_group.issued_on
        data['course_name'] = course_name
        CertificationGroup.objects.create_group_and_credentials(
            user_from=user_from,
            related_objects_list=consultant_role_group.consultant_roles.all(),
            **data
        )
