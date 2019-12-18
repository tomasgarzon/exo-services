from django.apps import apps
from django.db.models.signals import post_save, post_delete

from project.signals_define import project_post_launch

from .group import (
    project_launch_handler, new_team_handler, delete_group_handler,
    delete_team_handler)
from .roles import (
    user_project_role_handler,
    user_team_role_handler,
    delete_project_role_handler,
    delete_team_role_handler)


def setup_signals():
    Group = apps.get_model('communication', 'Group')
    Project = apps.get_model('project', 'Project')
    UserProjectRole = apps.get_model('project', 'UserProjectRole')
    UserTeamRole = apps.get_model('team', 'UserTeamRole')
    Team = apps.get_model('team', 'Team')

    project_post_launch.connect(
        project_launch_handler,
        sender=Project)

    post_save.connect(
        new_team_handler,
        sender=Team)

    post_delete.connect(
        delete_group_handler,
        sender=Group)

    post_save.connect(
        user_project_role_handler,
        sender=UserProjectRole)
    post_save.connect(
        user_team_role_handler,
        sender=UserTeamRole)

    post_delete.connect(
        delete_project_role_handler,
        sender=UserProjectRole)
    post_delete.connect(
        delete_team_role_handler,
        sender=UserTeamRole)
    post_delete.connect(
        delete_team_handler,
        sender=Team)
