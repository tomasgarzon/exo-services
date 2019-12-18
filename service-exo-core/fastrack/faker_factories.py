from django.conf import settings

from project.faker_factories.faker_factory_project import FakeProjectFactory

from .models import FastrackSprint


class FakeFastrackFactory(FakeProjectFactory):
    """
        Creates a fake FastrackSprint.
    """
    duration = 0
    lapse = settings.PROJECT_LAPSE_NO_APPLY

    class Meta:
        model = FastrackSprint
