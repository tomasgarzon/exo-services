# -*- coding: utf-8 -*-
import factory
from factory import django

from django.conf import settings

from exo_role.models import CertificationRole

from ..models import ConsultantRole


class FakeConsultantRoleFactory(django.DjangoModelFactory):

    class Meta:
        model = ConsultantRole

    certification_role = factory.LazyAttribute(lambda o: CertificationRole.objects.get(
        code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS))
    consultant = factory.SubFactory('consultant.faker_factories.FakeConsultantFactory')
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
