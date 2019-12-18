from django.apps import apps
from django.db.models.signals import (
    m2m_changed,
    post_save,
    post_delete,
    pre_delete
)

from ..signals_define import signal_team_coach_updated
from .team_signals import (
    signal_update_team_coach,
    signal_create_team,
    signal_delete_team,
    signal_pre_delete_team
)
from .team_members_signals import signal_new_member_added
from .team_step_handlers import (
    post_save_team_handler,
    post_save_step_handler)


def setup_signals():
    Team = apps.get_model(app_label='team', model_name='Team')
    Step = apps.get_model(app_label='project', model_name='Step')

    m2m_changed.connect(
        signal_new_member_added,
        sender=Team.team_members.through,
    )

    post_save.connect(signal_create_team, sender=Team)
    post_delete.connect(signal_delete_team, sender=Team)
    pre_delete.connect(signal_pre_delete_team, sender=Team)

    signal_team_coach_updated.connect(signal_update_team_coach)

    post_save.connect(post_save_step_handler, sender=Step)
    post_save.connect(post_save_team_handler, sender=Team)
