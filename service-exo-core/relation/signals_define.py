from django.dispatch import Signal


signal_head_coach_created = Signal(providing_args=['relation'])
signal_head_coach_removed = Signal(providing_args=['relation'])
signal_user_assigned = Signal(providing_args=['project', 'user'])
signal_user_unassigned = Signal(providing_args=['project', 'user'])
consultant_activity_enabled = Signal(providing_args=['consultant_activity'])
consultant_activity_disabled = Signal(providing_args=['consultant_activity'])
add_user_exo_hub = Signal(providing_args=['user', 'exo_hub_code'])
remove_user_exo_hub = Signal(providing_args=['user', 'exo_hub_code'])
user_certified = Signal(providing_args=['user', 'consultant_role'])
signal_add_exo_consultant_role = Signal(
    providing_args=['project', 'user_from', 'consultant', 'exo_role_code'])
