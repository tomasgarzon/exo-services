from django.dispatch import Signal


signal_username_created = Signal(providing_args=['user'])
signal_username_updated = Signal(providing_args=['user'])
email_verified = Signal(providing_args=['instance'])
signal_password_updated = Signal(providing_args=['instance', 'password'])

signal_exo_accounts_user_created = Signal(
    providing_args=['instance', 'from_user', 'user',
                    'send_notification', 'autosend', 'status'])

signal_exo_user_request_new_password = Signal(
    providing_args=['recipients', 'token', 'cipher_email', 'name'])

signal_exo_user_new_email_address_unverified = Signal(
    providing_args=['recipients', 'user_name', 'verify_link'])
