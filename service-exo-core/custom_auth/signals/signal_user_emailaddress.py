from django.conf import settings

from utils.mail import handlers


def request_user_emailadress_handler(sender, **kwargs):
    data = {
        'recipients': kwargs.get('recipients'),
        'user_name': kwargs.get('user_name'),
        'public_url': kwargs.get('verify_link'),
    }
    handlers.mail_handler.send_mail(
        'verification_email_address',
        **data)


def change_password_handler(sender, **kwargs):
    data = {
        'recipients': kwargs.get('recipients'),
        'name': kwargs.get('name')
    }
    token = kwargs.get('token')
    cipher_email = kwargs.get('cipher_email')

    data['public_url'] = settings.FRONTEND_PASSWORD_RESET_PAGE.format(
        **{'token': token, 'cipher_email': cipher_email})

    handlers.mail_handler.send_mail(
        'accounts_change_password',
        **data)
