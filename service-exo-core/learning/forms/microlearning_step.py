from django import forms
from django.forms import modelformset_factory

from ..models import MicroLearning


class MicroLearningForm(forms.ModelForm):

    class Meta:
        model = MicroLearning
        fields = [
            'typeform_url',
            'description',
        ]

    def clean_typeform_url(self):
        typeform_url = self.cleaned_data['typeform_url']
        return typeform_url.split('?')[0]


MicroLearningFactory = modelformset_factory(
    MicroLearning, form=MicroLearningForm, extra=0,
)
