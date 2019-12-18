from django.apps import apps
from django.db.models.signals import post_save, pre_delete

from .team_created import (
    when_team_post_save,
    when_team_pre_delete,
)

from .assignment_step import when_assignment_step_post_save


def setup_signals():
    # Models
    Team = apps.get_model(app_label='team', model_name='Team')
    AssignmentStep = apps.get_model(app_label='assignment', model_name='AssignmentStep')

    # Team Signals
    post_save.connect(when_team_post_save, sender=Team)
    pre_delete.connect(when_team_pre_delete, sender=Team)
    # Assignment Signals
    post_save.connect(when_assignment_step_post_save, sender=AssignmentStep)
