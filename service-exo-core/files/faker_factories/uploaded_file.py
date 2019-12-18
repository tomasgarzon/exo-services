import factory
from factory import django

from utils.faker_factory import faker

from ..models import UploadedFile


class FakeUploadedFileFactory(django.DjangoModelFactory):

    class Meta:
        model = UploadedFile

    created_by = factory.SubFactory(
        'exo_accounts.test_mixins.faker_factories.FakeUserFactory')
    filename = factory.LazyAttribute(lambda x: faker.word())
    mimetype = factory.LazyAttribute(lambda x: faker.mime_type())

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overriden attrs."""
        visibility = kwargs.pop('visibility', [])

        instance = super().create(**kwargs)

        if visibility:
            visibility_related = instance.get_visibility_relation()
            visibility_related.visibility = visibility
            visibility_related.save(update_fields=['visibility'])

        return instance
