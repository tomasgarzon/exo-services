import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth import get_user_model

from exo_role.models import ExORole
from populate.populator.common.helpers import find_tuple_values
from data import paths
from utils.populator import CommandYAMLMixin
from team.models import ProjectTeamRole
from utils.microlearning_helper import fix_weekly_quiz

from ...models import Project, ProjectRole, ProjectSettings


logger = logging.getLogger('service')


class Command(CommandYAMLMixin, BaseCommand):
    project = None

    def add_arguments(self, parser):
        parser.add_argument('pk', nargs='+', type=int)

    def create_project_settings(self):
        ProjectSettings.objects.get_or_create(project=self.project)

    def populate_steps(self, steps_template):
        call_command('populate_steps', self.project.pk, steps_template)

    def populate_assignments(self, assignments_template):
        call_command('populate_assignments', '-p', self.project.pk, '-t', assignments_template, '-d', '1')

    def populate_roles(self, roles):
        for index, role in enumerate(roles):
            exo_role = ExORole.objects.filter(code=role.get('code')).first()
            ProjectRole.objects.update_or_create(
                role=role.get('name'),
                level=role.get('level'),
                groups=role.get('team_communication_groups'),
                code=role.get('code'),
                exo_role=exo_role,
                order=index,
                project=self.project,
                defaults={'default': True})

    def populate_roles_team(self, roles):
        for role in roles:
            ProjectTeamRole.objects.update_or_create(
                role=role.get('name'),
                level=role.get('level'),
                code=role.get('code'),
                project=self.project,
                defaults={'default': True})

    def populate_streams(self, streams):
        for stream in streams:
            name = stream.get('name')
            code = find_tuple_values(
                settings.UTILS_STREAM_CH_TYPE,
                name)[0]
            new_stream = self.project.streams.create(name=name, code=code)
            for i in range(stream.get('num_team', 0)):
                self.project.teams.create(
                    created_by=self.project.created_by,
                    name='{} {}'.format(name, i),
                    stream=new_stream)

    def populate_settings(self, settings):
        project_settings = self.project.settings
        project_settings.team_communication = settings.get('team_communication')
        project_settings.ask_to_ecosystem = settings.get('ask_to_ecosystem')
        project_settings.launch['send_welcome_consultant'] = settings.get('send_welcome_consultant')
        project_settings.launch['send_welcome_participant'] = settings.get('send_welcome_participant')
        project_settings.launch['default_password'] = get_user_model().objects.make_random_password()
        project_settings.save()

    def get_yml_content(self):
        filepath = paths.PROJECT_TEMPLATES_PATH.format(self.project.content_template)
        return self.load_file(filepath)

    def log_error(self, exc):
        logger.error('Project populator error: {}'.format(exc))

    def handle(self, *args, **kwargs):
        self.project = Project.objects.get(pk=kwargs.get('pk')[0])
        logger.info('Project populator: {}'.format(self.project.name))
        self.create_project_settings()

        try:
            content = self.get_yml_content()
            self.populate_streams(content.get('streams'))
            if content.get('steps'):
                self.populate_steps(content.get('steps'))
                self.populate_assignments(content.get('assignments'))
            self.populate_roles(content.get('roles'))
            self.populate_roles_team(content.get('roles_team'))
            self.populate_settings(content.get('settings'))
            if not settings.IS_PRODUCTION:
                fix_weekly_quiz(self.project)
        except FileNotFoundError as exc:  # noqa
            self.log_error(exc)
        logger.info('Project populator finished')
