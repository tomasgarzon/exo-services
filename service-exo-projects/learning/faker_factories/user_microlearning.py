import factory
from factory import django

from ..models import UserMicroLearning


class FakeUserMicroLearningFactory(django.DjangoModelFactory):

    class Meta:
        model = UserMicroLearning

    microlearning = factory.SubFactory('learning.faker_factories.microlearning.FakeMicroLearningFactory')
