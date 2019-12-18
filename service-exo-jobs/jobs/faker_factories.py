from django.utils import timezone

from datetime import timedelta
import factory
import factory.fuzzy
from exo_role.models import ExORole

from utils.faker_factory import faker

from .models import Job


class FakeJobFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=20))
    exo_role = factory.Iterator(ExORole.objects.all())
    start = timezone.now()
    end = (timezone.now() + timedelta(days=5))
    status = 'UP'
    url = factory.LazyAttribute(lambda x: faker.uri())

    class Meta:
        model = Job

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if 'category' not in kwargs:
            kwargs['category'] = kwargs.get('exo_role').categories.first()
        return super()._create(model_class, *args, **kwargs)
