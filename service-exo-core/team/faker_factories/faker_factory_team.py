# -*- coding: utf-8 -*-
import factory
from factory import django, fuzzy

from utils.faker_factory import faker

from ..conf import settings
from ..models import Team


class FakeTeamFactory(django.DjangoModelFactory):

    class Meta:
        model = Team

    project = factory.SubFactory('project.faker_factories.FakeProjectFactory')
    coach = factory.SubFactory('consultant.faker_factories.FakeConsultantFactory')
    created_by = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')

    name = factory.LazyAttribute(lambda x: faker.word() + faker.numerify())

    stream = fuzzy.FuzzyChoice(
        [x[0] for x in settings.PROJECT_STREAM_CH_TYPE],
    )

    user_from = factory.SubFactory('exo_accounts.test_mixins.faker_factories.FakeUserFactory')

    @factory.post_generation
    def team_members(self, created, extracted, **kwargs):
        if not created:
            return None
        if extracted:
            members = [
                {'short_name': member.short_name, 'email': member.email}
                for member in extracted
            ]
            self.update_members(self.created_by, members)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        user_from = kwargs.get('user_from')
        project = kwargs.get('project')
        name = kwargs.get('name')
        coach = kwargs.get('coach')
        stream = kwargs.get('stream')
        created_by = kwargs.get('created_by')
        zoom_id = kwargs.get('zoom_id', None)
        return manager.create(
            user_from, project, name, coach,
            stream=stream,
            created_by=created_by,
            zoom_id=zoom_id,
        )
