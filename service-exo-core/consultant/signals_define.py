from django.dispatch import Signal


signal_update_consultant_status = Signal(providing_args=['consultant'])
consultant_post_activated = Signal(providing_args=['consultant'])
consultant_post_deactivated = Signal(providing_args=['consultant'])
consultant_profile_post_save = Signal(
    providing_args=['consultant', 'fields_name'],
)
