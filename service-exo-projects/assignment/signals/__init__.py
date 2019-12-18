from django.apps import apps
from django.db.models.signals import post_save, m2m_changed
from team.signals_define import stream_changed

from .team import post_save_team, post_stream_changed
from .assignment import post_save_assignment


def setup_signals():
    # Models
    Team = apps.get_model(app_label='team', model_name='Team')
    AssignmentStep = apps.get_model(app_label='assignment', model_name='AssignmentStep')

    # Team Signals
    post_save.connect(post_save_team, sender=Team)
    stream_changed.connect(post_stream_changed, sender=Team)

    # Assignment Signals
    m2m_changed.connect(
        post_save_assignment, sender=AssignmentStep.streams.through)
