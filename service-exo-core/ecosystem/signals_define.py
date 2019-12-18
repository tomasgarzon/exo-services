from django.dispatch import Signal


post_save_consultant_signal = Signal(providing_args=['consultant'])
ecosystem_member_created_signal = Signal(providing_args=['member'])
projects_ecosystem_changed = Signal(providing_args=['user'])
