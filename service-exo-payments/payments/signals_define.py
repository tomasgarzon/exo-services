from django.dispatch import Signal


signal_payment_received = Signal(providing_args=['payment'])
payment_status_changed = Signal(providing_args=['payment'])
