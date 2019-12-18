# -*- coding: utf-8 -*-
# Third Party Library
import factory
from factory import django

from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from .consultant_faker import FakeConsultantFactory
from ..models import ConsultantValidation, ConsultantValidationStatus
from ..conf import settings


class FakeConsultantValidationStatusFactory(django.DjangoModelFactory):
    """
        Creates a fake consultant.
    """

    class Meta:
        model = ConsultantValidationStatus

    validation = factory.Iterator(ConsultantValidation.objects.all())
    consultant = factory.SubFactory(FakeConsultantFactory)
    user_from = factory.SubFactory(FakeUserFactory)
    status = factory.fuzzy.FuzzyChoice(
        [x[0] for x in settings.CONSULTANT_VALIDATION_CH_STATUS],
    )
