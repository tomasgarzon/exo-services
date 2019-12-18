from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages

from utils.forms import CustomModelForm
from exo_accounts.models import EmailAddress


class UserChangeForm(CustomModelForm):
    current_email = forms.EmailField(
        label='Email', widget=forms.EmailInput(
            attrs={
                'data-url': reverse_lazy('api:accounts:validate-email'),
                'placeholder': 'Type your email',
            },
        ),
    )

    class Meta:
        model = get_user_model()
        fields = [
            'short_name', 'full_name',
            'about_me',
            'short_me',
            'bio_me',
            'phone',
        ]
        labels = {
            'about_me': 'Short Bio',
            'short_me': 'Shortline',
            'bio_me': 'Extended bio',
        }
        help_texts = {
            'short_me': 'Please write 2-4 words that sum up your profile, purpose, and/or line of work.\
            \nThis will be displayed publicly.',
            'about_me': 'Please provide a short bio (max 600 words). This will be displayed publicly.',
            'bio_me': 'Please provide an extended bio. This will be displayed publicly.',
        }
        placeholders = {
            'short_name': 'Type your short name',
            'full_name': 'Type your full name',
        }
        widgets = {
            'short_me': forms.TextInput,
        }

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super().__init__(*args, **kwargs)

    def clean_current_email(self):
        email = self.cleaned_data.get('current_email', '')
        if email:
            status, code = EmailAddress.objects.check_email(self.instance, email)
            if not status and code == settings.EXO_ACCOUNTS_VALIDATION_CHOICES_OTHER_USER:
                raise forms.ValidationError(
                    settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))
        return email

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        if 'current_email' in self.changed_data:
            status, code = EmailAddress.objects.change_user_email(
                user_from=self.context.get('user'),
                user=self.instance,
                email=self.cleaned_data.get('current_email'),
            )
            if status:
                # email verified previously or is an admin user
                if code in [settings.EXO_ACCOUNTS_VALIDATION_CHOICES_VERIFIED, '']:
                    code = settings.EXO_ACCOUNTS_VALIDATION_CHOICES_VERIFIED
                    messages.success(
                        self.context.get('request'),
                        settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))
                else:
                    code = settings.EXO_ACCOUNTS_VALIDATION_CHOICES_PENDING
                    messages.success(
                        self.context.get('request'),
                        settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))

            else:
                code = settings.EXO_ACCOUNTS_VALIDATION_CHOICES_NOT_VERIFIED
                messages.success(
                    self.context.get('request'),
                    settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))
        return instance


class UserProfileForm(UserChangeForm):
    pass
