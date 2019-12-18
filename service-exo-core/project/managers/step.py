from django.db import models
from django.core.management import call_command

from utils.dates import generate_dates

from ..queryset.step import StepQuerySet


class StepManager(models.Manager):

    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = StepQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def start_steps(self, project):
        project_steps = self.filter(project=project)
        dates = generate_dates(
            start_date=project.start,
            dates_number=project.duration,
            lapse=project.lapse,
            timezone=project.timezone,
        )

        for step, date in zip(project_steps, dates):
            step.start_step(date)

    def create_steps_from_data(self, project, step_info):
        for index in range(project.duration):
            name = step_info.get('name') % (index + 1)
            self.create(
                name=name,
                index=index + 1,
                project=project,
            )

    def create_steps_from_template(self, project, template_name):
        call_command('populate_steps', project.pk, template_name)

    def create_steps(self, project, *args, **kwargs):
        steps_template = project.customize.get('steps')
        step_info = steps_template.get('data')
        if step_info:
            self.create_steps_from_data(project, step_info)
        elif steps_template.get('template'):
            self.create_steps_from_template(project, steps_template.get('template'))

    def update_steps(self, project):
        # we have to remove steps, the latests
        if project.steps.count() > project.duration:
            old_steps = list(project.steps.all())[project.duration - project.steps.count():]
            for k in old_steps:
                k.delete()
        elif project.steps.count() < project.duration:
            # we have to create a new one
            steps_template = project.customize.get('steps')
            step = steps_template.get('data')
            new_steps = range(project.steps.count(), project.duration)
            for index in new_steps:
                name = step.get('name') % (index + 1)
                new_step = self.model(
                    name=name,
                    index=index + 1,
                    project=project,
                )
                new_step.save()
            if project.start:
                self.start_steps(project)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_sprint(self, sprint):
        return self.get_queryset().filter_by_sprint(sprint)

    def filter_by_lapse(self, lapse):
        return self.get_queryset().filter_by_lapse(lapse)

    def filter_by_index_range(self, start, end):
        return self.get_queryset().filter_by_index_range(start, end)
