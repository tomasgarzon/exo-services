# -*- coding: utf-8 -*-
import factory

from factory import django, fuzzy

from utils.faker_factory import faker
from utils.dates import string_to_timezone

from exo_role.models import ExORole

from ..models import Project, UserProjectRole, ProjectRole
from ..conf import settings


class FakeProjectFactory(django.DjangoModelFactory):

    class Meta:
        model = Project

    uuid = factory.LazyAttribute(lambda x: faker.uuid4())
    name = factory.LazyAttribute(lambda x: faker.word())
    description = factory.LazyAttribute(lambda x: faker.text())
    start = factory.LazyAttribute(lambda x: faker.date_time(tzinfo=string_to_timezone('utc')))
    location = factory.LazyAttribute(lambda x: '{}, {}'.format(faker.city(), faker.country()))
    status = settings.PROJECT_CH_STATUS_DRAFT
    content_template = settings.PROJECT_CH_PROJECT_TEMPLATE_DEFAULT
    customer = factory.LazyAttribute(lambda x: faker.company())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        if not kwargs.get('created_by'):
            raise Exception('User is required')
        return manager.create_project(*args, **kwargs)


class FakeProjectRoleFactory(django.DjangoModelFactory):
    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    level = fuzzy.FuzzyChoice(dict(settings.PROJECT_ROLE_LEVEL).keys())
    groups = fuzzy.FuzzyChoice(dict(settings.PROJECT_CH_GROUP_CHOICES).keys())
    exo_role = exo_role = factory.LazyAttribute(lambda o: ExORole.objects.get(
        code=settings.EXO_ROLE_CODE_ADVISOR))
    role = factory.LazyAttribute(lambda o: o.exo_role.code)
    code = factory.LazyAttribute(lambda o: o.exo_role.code)

    class Meta:
        model = ProjectRole


class FakeUserProjectFactory(django.DjangoModelFactory):
    project_role = factory.SubFactory('project.faker_factories.FakeProjectRoleFactory')
    active = True

    class Meta:
        model = UserProjectRole
