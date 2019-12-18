from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase

from exo_role.models import CertificationRole

from consultant.faker_factories import FakeConsultantFactory
from custom_auth.faker_factories import FakeInternalOrganizationFactory
from relation.models import ConsultantRole

from ..models import User
from ..test_mixins import SuperUserTestMixin, UserTestMixin
from ..test_mixins.faker_factories import FakeUserFactory

from utils.faker_factory import faker


class UserTest(SuperUserTestMixin,
               UserTestMixin,
               TestCase):

    def setUp(self):
        super().setUp()

    def test_user_title(self):
        # PREPARE DATA
        role_foundations = CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS)
        role_consultant = CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT)
        role_coach = CertificationRole.objects.get(code=settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH)

        regular_user = FakeUserFactory(is_active=True)
        consultant1 = FakeConsultantFactory.create(user__is_active=True)
        consultant2 = FakeConsultantFactory.create(user__is_active=True)
        organization = FakeInternalOrganizationFactory()
        position = ' '.join(faker.words())

        # DO ACTION
        organization.users_roles.create(
            user=consultant1.user,
            position=position,
            status=settings.RELATION_ROLE_CH_ACTIVE)
        ConsultantRole.objects.create(
            consultant=consultant1,
            certification_role=role_foundations,
        )
        ConsultantRole.objects.create(
            consultant=consultant1,
            certification_role=role_consultant,
        )
        ConsultantRole.objects.create(
            consultant=consultant1,
            certification_role=role_coach,
        )
        ConsultantRole.objects.create(
            consultant=consultant2,
            certification_role=role_foundations,
        )

        consultant1.refresh_from_db()
        consultant2.refresh_from_db()

        # ASSERTS
        self.assertIsNone(regular_user.user_title)
        self.assertTrue(organization.name in consultant1.user.user_title)
        self.assertTrue(position in consultant1.user.user_title)
        self.assertTrue(role_foundations.name in consultant1.user.user_title)
        self.assertTrue(role_consultant.name in consultant1.user.user_title)
        self.assertTrue(role_coach.name in consultant1.user.user_title)
        self.assertTrue(role_foundations.name in consultant2.user.user_title)

    def test_create_user(self):
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create_user(email=user_email,
                                        password=user_pwd,
                                        short_name=faker.first_name())
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.has_usable_password())
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_default_create_user(self):
        # ##
        # By default set a NOT USABLE password
        # ##

        user = User.objects.create_user(email=faker.email(),
                                        short_name=faker.first_name())

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.can_authenticate)

    def test_create_user_active(self):
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create_user(email=user_email,
                                        password=user_pwd,
                                        is_active=True,
                                        short_name=faker.first_name())
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertTrue(user.can_authenticate)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_create_superuser(self):
        """
        Users admin should be active users always
        """
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create_superuser(email=user_email,
                                             password=user_pwd,
                                             short_name=faker.first_name())
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_get_or_create(self):
        name = faker.first_name()
        email = faker.email()
        user, created = User.objects.get_or_create(email=email,
                                                   defaults={'short_name': name})
        self.assertTrue(created)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.short_name, name)
        self.assertTrue(user.has_usable_password())
        user2 = User.objects.get_or_create(email=faker.email(),
                                           defaults={'short_name': faker.first_name()})
        self.assertIsNotNone(user2)
        user3, created = User.objects.get_or_create(
            email=faker.email(),
            defaults={
                'short_name': name,
                'full_name': '{} {}'.format(faker.first_name(), faker.last_name()),
                'is_active': True,
                'password': name
            })
        self.assertIsNotNone(user3)
        self.assertTrue(created)
        self.assertNotEqual(user3.full_name, '')
        self.assertTrue(user3.has_usable_password())
        self.assertTrue(user3.is_active)
        self.assertTrue(user3.check_password(name))
        user4, created = User.objects.get_or_create(email=email)
        self.assertFalse(created)
        self.assertEqual(user4.id, user.id)

    def test_create_username(self):
        user_regular = FakeUserFactory(is_active=True)
        user_regular.generate_public_username()
        self.assertIsNotNone(user_regular.public_username)
        self.assertNotEqual(user_regular.public_username, '')
        user2 = FakeUserFactory(is_active=True, full_name=user_regular.full_name)
        user2.generate_public_username()
        self.assertNotEqual(user_regular.public_username, user2.public_username)

    def test_get_or_create_several_emailaddress(self):
        name = faker.first_name()
        email = faker.email()
        user, created = User.objects.get_or_create(email=email,
                                                   defaults={'short_name': name})
        self.assertTrue(created)
        email2 = faker.email()
        user.add_email_address(email2)
        user2, created = User.objects.get_or_create(
            email=email2,
            defaults={'short_name': name})
        self.assertFalse(created)
        self.assertEqual(user2.pk, user.pk)

    def test_default_value_password_updated(self):

        user_email = faker.email()
        user = get_user_model().objects.create_user(
            email=user_email,
            is_active=True,
            short_name=faker.first_name())

        self.assertFalse(user.password_updated)

        # Set a real password
        user.set_password(faker.word())
        self.assertTrue(user.password_updated)

        # Set a random password
        user.set_password(faker.word(), True)
        self.assertFalse(user.password_updated)

        # Set an unusable password
        user.set_unusable_password()
        self.assertFalse(user.password_updated)

        # Set a real password
        user.set_password(faker.word())
        self.assertTrue(user.password_updated)

    def test_user_is_empty_user(self):
        # PREPARE DATA
        test_cases = [
            [{'data': {'is_superuser': False,
                       'is_staff': False},
              'result': True}],
            [{'data': {'is_superuser': True,
                       'is_staff': False},
              'result': False}],
            [{'data': {'is_superuser': False,
                       'is_staff': True},
              'result': False}],
            [{'data': {'is_superuser': True,
                       'is_staff': True},
              'result': False}]]

        for index, test_case in enumerate(test_cases):
            # DO ACTIONS
            user = FakeUserFactory(**test_case[0].get('data'))

            # ASSERTIONS
            self.assertEqual(
                user.is_empty_user(),
                test_case[0].get('result'),
                'case {}'.format(index))

    def test_get_platform_languages(self):

        User = get_user_model()
        users = FakeUserFactory.create_batch(size=3)
        users_emails = [_.email for _ in users]
        retrieved_languages = User.objects \
                                  .get_platform_languages(users_emails)

        self.assertEqual(len(retrieved_languages), 1)
        self.assertTrue(settings.LANGUAGE_DEFAULT in retrieved_languages)

        user_1 = users[0]
        user_1.platform_language = settings.LANGUAGE_ES
        user_1.save()

        retrieved_languages = User.objects \
                                  .get_platform_languages(users_emails)

        self.assertEqual(len(retrieved_languages), 2)
        self.assertTrue(settings.LANGUAGE_DEFAULT in retrieved_languages)
        self.assertTrue(settings.LANGUAGE_ES in retrieved_languages)

        user_2 = users[1]
        user_2.platform_language = settings.LANGUAGE_PT
        user_2.save()

        retrieved_languages = User.objects \
                                  .get_platform_languages(users_emails)

        self.assertEqual(len(retrieved_languages), 3)
        self.assertTrue(settings.LANGUAGE_DEFAULT in retrieved_languages)
        self.assertTrue(settings.LANGUAGE_ES in retrieved_languages)
        self.assertTrue(settings.LANGUAGE_PT in retrieved_languages)
