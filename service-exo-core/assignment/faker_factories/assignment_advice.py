import factory

from factory import django

from ..models import AssignmentAdvice


class FakeAssignmentAdviceFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentAdvice

    block = factory.SubFactory('assignment.faker_factories.assignment.InformationBlockFactory')
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
