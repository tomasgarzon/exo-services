from django.apps import apps
from django.db.models.signals import post_save, post_delete

from project.signals_define import project_post_launch

from .opportunity import (
    project_launch_handler, new_team_handler,
    post_advisor_request_save,
    user_team_role_handler,
    delete_team_handler)


def setup_signals():
    AdvisorRequestSettings = apps.get_model('opportunities', 'AdvisorRequestSettings')
    Project = apps.get_model('project', 'Project')
    Team = apps.get_model('team', 'Team')
    UserTeamRole = apps.get_model('team', 'UserTeamRole')

    project_post_launch.connect(
        project_launch_handler,
        sender=Project)
    post_save.connect(
        new_team_handler,
        sender=Team)
    post_delete.connect(
        delete_team_handler,
        sender=Team)
    post_save.connect(
        post_advisor_request_save,
        sender=AdvisorRequestSettings)
    post_save.connect(
        user_team_role_handler,
        sender=UserTeamRole)
