import factory
import factory.fuzzy

from utils.faker_factory import faker

from ..models import Applicant


class FakeApplicantFactory(factory.django.DjangoModelFactory):

    summary = factory.LazyAttribute(lambda x: faker.text())
    questions_extra_info = factory.LazyAttribute(lambda x: faker.text())

    class Meta:
        model = Applicant

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        if not kwargs.get('opportunity'):
            raise Exception('Opportunity is required')
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_open_applicant(*args, **kwargs)
