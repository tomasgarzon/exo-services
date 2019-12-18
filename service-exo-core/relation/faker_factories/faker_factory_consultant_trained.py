# -*- coding: utf-8 -*-
import factory
from factory import django

from ..models import ConsultantTrained


class FakeConsultantTrainedFactory(django.DjangoModelFactory):

    class Meta:
        model = ConsultantTrained

    training_session = factory.SubFactory('learning.faker_factories.FakeTrainingSessionFactory')
    consultant = factory.SubFactory('consultant.faker_factories.FakeConsultantFactory')
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
