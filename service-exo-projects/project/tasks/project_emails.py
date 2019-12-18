from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model

from celery import Task

from utils.mails.handlers import mail_handler

from ..mails import (
    LocationChanged, ProjectDateChanged, StepDateChanged,
    UserAddedTeamChanged, RoleRemoved, RoleChanged
)


class ProjectLocationChangedTask(Task):
    name = 'ProjectLocationChangedTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        for user in project.members:
            user_data = LocationChanged(project, user).get_data()
            email_name = settings.PROJECT_EMAIL_LOCATION_CHANGED
            mail_handler.send_mail(
                template=email_name,
                recipients=[user_data.pop('email')],
                **user_data)


class ProjectStartChangedTask(Task):
    name = 'ProjectStartChangedTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        for user in project.members:
            user_data = ProjectDateChanged(project, user).get_data()
            email_name = settings.PROJECT_EMAIL_START_CHANGED
            mail_handler.send_mail(
                template=email_name,
                recipients=[user_data.pop('email')],
                **user_data)


class StepStartChangedTask(Task):
    name = 'StepStartChangedTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Step = apps.get_model('project', 'Step')
        step = Step.objects.get(pk=kwargs.get('step_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        for user in step.project.members:
            user_data = StepDateChanged(step, user).get_data()
            email_name = settings.PROJECT_EMAIL_START_CHANGED
            mail_handler.send_mail(
                template=email_name,
                recipients=[user_data.pop('email')],
                **user_data)


class MemberAddedTeamTask(Task):
    name = 'MemberAddedTeamTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Team = apps.get_model('team', 'Team')
        team = Team.objects.get(pk=kwargs.get('team_id'))
        user = get_user_model().objects.get(pk=kwargs.get('user_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        user_data = UserAddedTeamChanged(team, user).get_data()
        email_name = settings.PROJECT_EMAIL_MEMBER_ADDED_TEAM
        mail_handler.send_mail(
            template=email_name,
            recipients=[user_data.pop('email')],
            **user_data)


class MemberRemovedTask(Task):
    name = 'MemberRemovedTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        roles = kwargs.get('roles', '')
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))
        user = get_user_model().objects.get(pk=kwargs.get('user_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        user_data = RoleRemoved(project, roles, user).get_data()
        email_name = settings.PROJECT_EMAIL_MEMBER_REMOVED
        mail_handler.send_mail(
            template=email_name,
            recipients=[user_data.pop('email')],
            **user_data)


class RolesChangedTask(Task):
    name = 'RolesChangedTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        project = Project.objects.get(pk=kwargs.get('project_id'))
        user = get_user_model().objects.get(pk=kwargs.get('user_id'))

        if settings.POPULATOR_MODE and not settings.TEST_MODE:
            return
        user_data = RoleChanged(project, user).get_data()
        email_name = settings.PROJECT_EMAIL_ROLE_CHANGED
        mail_handler.send_mail(
            template=email_name,
            recipients=[user_data.pop('email')],
            **user_data)
