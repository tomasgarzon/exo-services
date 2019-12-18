from django.dispatch import Signal


set_null_signal = Signal(providing_args=['instance'])

edit_slug_field = Signal(
    providing_args=['instance', 'previous_value', 'new_value', 'tag_model'],
)
