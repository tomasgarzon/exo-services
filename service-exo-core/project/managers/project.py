from django.db import models
from django.apps import apps
from django.conf import settings

from utils.descriptors import CustomFilterDescriptorMixin
from custom_auth.helpers import UserProfileWrapper

from ..queryset.project import ProjectQuerySet


class ProjectManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    queryset_class = ProjectQuerySet

    FILTER_DESCRIPTORS = [{
        'field': 'type',
        'options': settings.PROJECT_CH_TYPE_PROJECT,
    }]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def create_generic_project(self, user_from, name, customer, duration, lapse):
        GenericProject = apps.get_model(
            app_label='generic_project',
            model_name='GenericProject',
        )

        generic_project = GenericProject.objects.create(
            created_by=user_from,
            internal_organization=UserProfileWrapper(user_from).organization,
            name=name,
            customer=customer,
            duration=duration,
            lapse=lapse,
        )

        return generic_project

    def create_sprint_automated(self, user_from, name, description, customer, duration):
        SprintAutomated = apps.get_model(
            app_label='sprint_automated',
            model_name='SprintAutomated',
        )

        sprint_automated = SprintAutomated.objects.create(
            created_by=user_from,
            internal_organization=UserProfileWrapper(user_from).organization,
            lapse=settings.PROJECT_LAPSE_PERIOD,
            name=name,
            description=description,
            customer=customer,
            duration=duration
        )

        return sprint_automated

    def filter_by_type(self, project_type):
        return self.get_queryset().filter_by_type(project_type)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_user_or_organization(self, user):
        return self.get_queryset().filter_by_user_or_organization(user)

    def filter_actives(self, from_datetime=None):
        return self.get_queryset().actives(from_datetime)

    def filter_finished(self, from_datetime=None):
        return self.get_queryset().finished(from_datetime)

    def exclude_draft(self):
        return self.get_queryset().exclude_draft()
