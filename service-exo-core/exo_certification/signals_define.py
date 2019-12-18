from django.dispatch import Signal

certification_request_payment_success = Signal(providing_args=['pk'])
certification_request_status_updated = Signal(providing_args=['pk'])
