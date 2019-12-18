from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin

from ..tasks import (
    ProjectLocationTask, ProjectLocationChangedTask,
    ProjectStartChangedTask,
)
from ..queryset.project import ProjectQuerySet
from ..conf import settings
from ..signals_define import project_created_signal, project_started_changed


class ProjectManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    queryset_class = ProjectQuerySet

    FILTER_DESCRIPTORS = [{
        'field': 'template',
        'options': settings.PROJECT_CH_PROJECT_TEMPLATE,
    }, {
        'field': 'status',
        'options': settings.PROJECT_CH_STATUS,
    }]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_uuid(self, uuid):
        return self.get_queryset().filter_by_uuid(uuid)

    def filter_by_template(self, template):
        return self.get_queryset().filter_by_template(template)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_actives(self, from_datetime=None):
        return self.get_queryset().actives(from_datetime)

    def filter_finished(self, from_datetime=None):
        return self.get_queryset().finished(from_datetime)

    def exclude_training(self):
        return self.get_queryset().exclude_training()

    def exclude_draft(self):
        return self.get_queryset().exclude_draft()

    def create_project(self, *args, **kwargs):
        project = super().create(**kwargs)
        project.statuses.create(created_by=project.created_by, status=project.status)
        ProjectLocationTask().s(project_id=project.id).apply_async()
        project_created_signal.send(
            sender=project.__class__,
            project=project)
        return project

    def update_project(self, instance, **kwargs):
        start_changed = instance.start != kwargs.get('start')
        location_changed = instance.location != kwargs.get('location')

        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        if start_changed:
            project_started_changed.send(
                sender=instance.__class__,
                instance=instance)
        if location_changed and not instance.is_draft:
            ProjectLocationChangedTask().s(project_id=instance.id).apply_async()
        if start_changed and not instance.is_draft:
            ProjectStartChangedTask().s(project_id=instance.id).apply_async()
        ProjectLocationTask().s(project_id=instance.id).apply_async()
        return instance
