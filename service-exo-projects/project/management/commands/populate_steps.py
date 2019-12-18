import logging

from django.core.management.base import BaseCommand
from django.conf import settings as django_settings

from data import paths
from utils.populator import CommandYAMLMixin
from learning.models import MicroLearning

from ...models import Project, Step

logger = logging.getLogger('django')


class Command(CommandYAMLMixin, BaseCommand):
    model = Step

    def __init__(self, *args, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)

    def get_filename(self, template):
        return paths.PROJECT_STEPS_PATH.format(template)

    def add_arguments(self, parser):
        parser.add_argument('project_pk', nargs='+', type=int)
        parser.add_argument('template', nargs='+', type=str)

    def clear_steps(self, project):
        self.model.objects.filter_by_project(project).delete()

    def load_project_setting(self, lapse, duration, project):
        project.lapse = lapse
        project.duration = duration
        project.save()

    def enable_quiz_for_project(self, project):
        settings = project.settings
        settings.participant_step_microlearning_enabled = True
        settings.save()

    def update_quiz_for_stream(self, step, stream, url):
        if url:
            step_stream = step.streams.get(stream__code=stream)
            microlearning, _ = MicroLearning.objects.update_or_create(
                step_stream=step_stream,
                defaults={'typeform_url': url},
            )

    def load_steps(self, steps, project):
        has_quiz = False
        for row_step in steps:
            step = self.model.objects.create(
                name=row_step.get('name'),
                index=row_step.get('index'),
                duration=row_step.get('duration', 1),
                project=project,
            )
            self.update_quiz_for_stream(
                step,
                django_settings.UTILS_STREAM_CH_CORE,
                row_step.get('core_quiz_url'),
            )
            self.update_quiz_for_stream(
                step,
                django_settings.UTILS_STREAM_CH_EDGE,
                row_step.get('edge_quiz_url'),
            )
            if row_step.get('core_quiz_url') or row_step.get('edge_quiz_url'):
                has_quiz = True
        if has_quiz:
            self.enable_quiz_for_project(project)

    def handle(self, *args, **kwargs):
        project_pk = kwargs.get('project_pk')[0]
        template_steps = kwargs.get('template')[0]
        project = Project.objects.get(pk=project_pk)
        filepath = self.get_filename(template_steps)

        self.clear_steps(project)
        try:
            content = self.load_file(filepath)
            self.load_project_setting(
                lapse=content.get('lapse'),
                duration=content.get('total'),
                project=project,
            )
            self.load_steps(
                steps=content.get('steps'),
                project=project,
            )
        except FileNotFoundError as exc:  # noqa
            message = '{} - populate steps'.format(exc)
            self.logger.error(message)
