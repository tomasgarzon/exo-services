from django import forms
from django.contrib.auth import get_user_model

from exo_accounts.utils.util import normalize_email


class ConsultantAddForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Type ExO Consultant email',
                'maxlength': 255,
            },
        ),
    )

    name = forms.CharField(
        label='Full name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Type ExO Consultant name',
                'maxlength': 30,
            },
        ),
    )

    coins = forms.IntegerField(
        label='ExO Coins',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Type ExO coins',
                'maxlength': 30,
            },
        ),
    )

    waiting_list = forms.BooleanField(
        label='Add to waiting list',
        required=False)

    custom_text = forms.CharField(
        label='Custom text',
        required=False,
        widget=forms.Textarea(
            attrs={'placeholder': 'Write a personal text to be added to the invitation'},
        ),
    )

    def clean_email(self):
        email = normalize_email(self.cleaned_data.get('email'))
        user = get_user_model().objects.filter(email=email)
        if user.exists():
            user = user.get()
            if user.is_consultant:
                raise forms.ValidationError('A consultant already exists with this email')
        return email
