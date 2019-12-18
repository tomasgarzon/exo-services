from django.dispatch import Signal


signal_website_update = Signal(providing_args=['instance'])
