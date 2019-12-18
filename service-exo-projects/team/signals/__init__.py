from django.apps import apps
from django.db.models.signals import (
    post_save,
    post_delete,
)
from reversion.signals import post_revision_commit

from .team_step_handlers import (
    post_save_team_handler,
    post_save_step_handler)
from .user_team_role  import (
    post_save_user_team_role,
    post_delete_user_team_role)
from .team import post_save_team


def setup_signals():
    Team = apps.get_model(app_label='team', model_name='Team')
    Step = apps.get_model(app_label='project', model_name='Step')
    UserTeamRole = apps.get_model(
        app_label='team', model_name='UserTeamRole')


    post_save.connect(post_save_step_handler, sender=Step)
    post_save.connect(post_save_team_handler, sender=Team)

    post_save.connect(post_save_user_team_role, sender=UserTeamRole)
    post_delete.connect(post_delete_user_team_role, sender=UserTeamRole)

    post_revision_commit.connect(post_save_team)
