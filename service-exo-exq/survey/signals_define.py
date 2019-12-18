from django.dispatch import Signal

post_survey_filled = Signal(providing_args=['instance'])
