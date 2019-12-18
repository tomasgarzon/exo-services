import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from ...models import Project

logger = logging.getLogger('service')


class Command(BaseCommand):

    def update_project_status(self):
        for project in Project.objects.exclude(status=settings.PROJECT_CH_STATUS_FINISHED):
            if project.is_waiting and project.start == timezone.now().date():
                project.set_start(project.created_by)
            elif project.is_started and project.end == timezone.now().date():
                project.set_finish(project.created_by)

    def update_step_status(self):
        for project in Project.objects.filter(status=settings.PROJECT_CH_STATUS_STARTED):
            current_step = project.current_step()
            current_step.set_current()
            for previous_step in project.steps.filter(index__lt=current_step.index):
                previous_step.set_past()
            for previous_step in project.steps.filter(index__gt=current_step.index):
                previous_step.set_future()

    def handle(self, *args, **kwargs):
        self.update_project_status()
        self.update_step_status()
