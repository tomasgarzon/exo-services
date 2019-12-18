from django.contrib.auth.forms import PasswordResetForm
from django import forms
from django.conf import settings

from .models import EmailAddress


class UserResetPasswordForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.error_messages = {
            'not-registered': 'This email address doesn\'t exist in ' + settings.BRAND_NAME,
            'not-usable-password': 'Please contact support to enable your Lever account'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            email_address = EmailAddress.objects.get(email__iexact=email)
        except EmailAddress.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages.get('not-registered'),
            )
        user = email_address.user
        if not user.has_usable_password():
            raise forms.ValidationError(
                self.error_messages.get('not-usable-password'),
            )
        return email.lower()

    def get_users(self, email):
        """
        Override the get_users forms from PasswordResetForm to make
        possible to send emails using EmailAddress entities
        """
        active_users = EmailAddress.objects.filter(
            email__iexact=email,
        )
        return (u.user for u in active_users if u.user.has_usable_password())

    def send_mail(
        self, subject_template_name, email_template_name,
        context, from_email, to_email,
        html_email_template_name=None,
    ):
        EmailAddress.objects.get(
            email__iexact=to_email,
        ).user.send_notification_change_password(
            self.cleaned_data.get('email'),
        )
