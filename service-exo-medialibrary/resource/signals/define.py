from django.dispatch import Signal

post_save_resource_signal = Signal(providing_args=['resource'])
