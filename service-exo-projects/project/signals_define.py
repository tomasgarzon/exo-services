from django.dispatch import Signal


project_created_signal = Signal(
    providing_args=['project'])
project_post_launch = Signal(
    providing_args=['project', 'user_from'])
user_project_role_activated = Signal(
    providing_args=['instance', 'user_from'])
project_started_changed = Signal(
    providing_args=['instance'])
step_started_changed = Signal(
    providing_args=['instance'])
