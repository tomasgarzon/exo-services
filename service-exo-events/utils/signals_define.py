from django.dispatch import Signal


add_user_exo_hub = Signal(providing_args=['user', 'exo_hub_code'])
remove_user_exo_hub = Signal(providing_args=['user', 'exo_hub_code'])
