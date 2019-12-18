from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import tag

from django.test import TestCase
from utils.faker_factory import faker
from core.models import Language
from partner.faker_factories import FakePartnerFactory
from registration.models import RegistrationProcess
from test_utils.test_case_mixins import SuperUserTestMixin

from ..faker_factories import (
    FakeConsultantFactory
)
from ..models import Consultant
from ..conf import settings


@tag('sequencial')
class ConsultantQuerySetTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()

    def test_filter_simple(self):
        first_name = faker.first_name()
        wrong_name = faker.numerify()
        language_esp = Language.objects.get(name='Spanish')
        language_eng = Language.objects.get(name='English')
        FakeConsultantFactory.create(
            user__short_name=first_name,
            languages=[language_esp],
        )
        FakeConsultantFactory.create(
            user__short_name=wrong_name,
            user__full_name=wrong_name,
            languages=[language_esp],
        )
        FakeConsultantFactory.create(
            user__short_name=wrong_name,
            user__full_name=wrong_name,
            languages=[language_eng],
        )
        filter = {'name': first_name}
        self.assertEqual(Consultant.all_objects.filter_complex(*filter, **filter).count(), 1)
        filter = {'language': language_esp}
        self.assertEqual(Consultant.all_objects.filter_complex(*filter, **filter).count(), 2)

    def test_filter_partner(self):
        partner = FakePartnerFactory.create()
        filter = {'partner': partner}
        FakeConsultantFactory.create_batch(size=3)
        self.assertEqual(Consultant.all_objects.filter_complex(*filter, **filter).count(), 0)

    def test_filter_status(self):

        FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_DISABLED)
        FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_DISABLED)
        c1 = FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION)
        c2 = FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION)

        filter = {'status': settings.CONSULTANT_STATUS_CH_ACTIVE}
        self.assertEqual(
            Consultant.all_objects.filter_complex(*filter, **filter).count(),
            1,
        )

        filter = {'status': settings.CONSULTANT_STATUS_CH_DISABLED}
        self.assertEqual(
            Consultant.all_objects.filter_complex(*filter, **filter).count(),
            2,
        )

        RegistrationProcess.create_process(
            self.super_user,
            c1.user,
        )
        RegistrationProcess.create_process(
            self.super_user,
            c2.user,
        )
        filter = {'status': settings.REGISTRATION_STEPS_NAMES[2][0]}
        self.assertEqual(
            Consultant.all_objects.filter_complex(*filter, **filter).count(),
            2,
        )

    def test_filter_by_name(self):
        first_name1 = faker.first_name() + faker.numerify()
        last_name1 = faker.last_name() + faker.numerify()
        first_name2 = faker.first_name() + faker.numerify()
        last_name2 = faker.last_name() + faker.numerify()
        FakeConsultantFactory.create(
            user__short_name=first_name1,
            user__full_name=last_name1,
        )
        FakeConsultantFactory.create(
            user__short_name=first_name2,
            user__full_name=last_name2,
        )
        FakeConsultantFactory.create(
            user__short_name=first_name1,
            user__full_name=last_name2,
        )
        FakeConsultantFactory.create(
            user__short_name=first_name2,
            user__full_name=last_name1,
        )

        queryset = Consultant.all_objects.all()
        filter = {'name': first_name1}
        self.assertEqual(queryset.filter_complex(*filter, **filter).count(), 2)
        filter = {'name': last_name2}
        self.assertEqual(queryset.filter_complex(*filter, **filter).count(), 2)
        filter = {'name': first_name1 + ' ' + last_name2}
        self.assertEqual(queryset.filter_complex(*filter, **filter).count(), 3)
        filter = {'name': first_name1 + ' ' + first_name2}
        self.assertEqual(queryset.filter_complex(*filter, **filter).count(), 4)

    def test_filter_by_permissions(self):

        language_contenttype = ContentType.objects.get_for_model(Language)
        consultant_1 = FakeConsultantFactory()
        consultant_2 = FakeConsultantFactory()
        new_perm_1 = Permission(
            name=faker.word() + faker.numerify(),
            codename=faker.word() + faker.numerify(),
            content_type=language_contenttype,
        )
        new_perm_1.save()
        new_perm_2 = Permission(
            name=faker.word() + faker.numerify(),
            codename=faker.word() + faker.numerify(),
            content_type=language_contenttype,
        )
        new_perm_2.save()

        self.assertEqual(
            Consultant.objects.filter_by_user_permissions(
                [new_perm_1.codename],
            ).count(),
            0,
        )

        consultant_1.user.user_permissions.add(new_perm_1)
        self.assertEqual(
            Consultant.objects.filter_by_user_permissions(
                [new_perm_1.codename],
            ).count(),
            1,
        )

        self.assertEqual(
            Consultant.objects.filter_by_user_permissions(
                [new_perm_1.codename, new_perm_2.codename],
            ).count(),
            0,
        )
        consultant_1.user.user_permissions.add(new_perm_2)
        consultant_2.user.user_permissions.add(new_perm_1)
        consultant_2.user.user_permissions.add(new_perm_2)

        self.assertEqual(
            Consultant.objects.filter_by_user_permissions(
                [
                    new_perm_1.codename,
                    new_perm_2.codename,
                ],
            ).count(),
            2,
        )
