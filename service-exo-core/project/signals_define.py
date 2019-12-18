from django.dispatch import Signal


edit_project_start_date = Signal(providing_args=['instance'])
project_post_launch = Signal(providing_args=['project', 'user'])
edit_project_duration_date = Signal(providing_args=['instance'])
project_status_signal = Signal(providing_args=['instance'])
project_category_changed_signal = Signal(providing_args=['instance'])
