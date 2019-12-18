from django.dispatch import Signal

microlearning_webhook_received_send = Signal(providing_args=['user_microlearning'])
