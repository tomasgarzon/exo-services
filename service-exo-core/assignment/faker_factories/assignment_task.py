import factory

from factory import django

from ..models import AssignmentTask


class FakeAssignmentTaskFactory(django.DjangoModelFactory):

    class Meta:
        model = AssignmentTask

    block = factory.SubFactory('assignment.faker_factories.assignment.InformationBlockFactory')
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')
