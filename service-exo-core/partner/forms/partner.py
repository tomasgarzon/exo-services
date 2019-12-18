from django import forms

from utils.forms import CustomModelForm

from ..models import Partner


class PartnerForm(CustomModelForm):

    class Meta:
        model = Partner
        exclude = [
            'users',
            'selectable_profile_picture',
            'slug',
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
            'name': 'Type partner name',
        }
