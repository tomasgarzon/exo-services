from django.dispatch import Signal

stream_changed = Signal(providing_args=['team'])
user_team_role_activated = Signal(
    providing_args=['instance', 'user_from'])
signal_post_overall_rating_team_step_save = Signal(
    providing_args=['user', 'team_step', 'relation_type'])
