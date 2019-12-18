from django import forms

from utils.forms import CustomModelForm
from partner.models import Partner

from ..models import Customer


class CustomerForm(CustomModelForm):

    partner = forms.ModelChoiceField(
        required=False,
        label='Partner',
        queryset=Partner.objects.all(),
        widget=forms.Select(
            attrs={'class': 'select2'},
        ),
    )

    class Meta:
        model = Customer
        exclude = [
            'users',
            'selectable_profile_picture',
            'contact_person',
            'customer_type',
            'slug',
            'partners',
        ]
        labels = {
            'name': 'Name',
            'profile_picture': 'Logo',
        }
        widgets = {
            'profile_picture': forms.FileInput(
                attrs={'class': 'hide'},
            ),
            'place_id': forms.HiddenInput()
        }
        placeholders = {
            'name': 'Type company name',
            'website': 'http://www.example.com',
        }
