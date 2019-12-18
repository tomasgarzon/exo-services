from django.dispatch import Signal


signal_team_coach_updated = Signal(providing_args=[
    'new_coach',
    'old_coach',
])

signal_post_overall_rating_team_step_save = Signal(
    providing_args=['consultant', 'team_step', 'relation_type'])
