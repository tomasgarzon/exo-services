# Third Party Library
import factory
from factory import django

from utils.faker_factory import faker

from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..models import Resource
from .tag import FakeTagFactory


class FakeResourceFactory(django.DjangoModelFactory):

    """
        Creates a fake consultant.
    """

    class Meta:
        model = Resource

    created_by = factory.SubFactory(FakeUserFactory)
    name = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
    description = factory.LazyAttribute(lambda x: faker.text())
    file = factory.django.FileField()
    link = factory.LazyAttribute(lambda x: faker.url())

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for tag in extracted:
                self.tags.add(tag)
        else:
            for tag in FakeTagFactory.create_batch(size=3):
                self.tags.add(tag)
