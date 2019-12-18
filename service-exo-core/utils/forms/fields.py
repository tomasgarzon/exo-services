from django import forms

from exo_accounts.models import EmailAddress
from exo_accounts.utils.util import normalize_email


class UserEmailAddressField(forms.EmailField):
    def clean(self, value):
        email = normalize_email(value)

        try:
            EmailAddress.objects.get(email__iexact=email)
        except EmailAddress.DoesNotExist:
            raise forms.ValidationError('Email DoesNotExist')

        return email
