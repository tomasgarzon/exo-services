from django import forms

from ..models import BulkCreation


class BulkCreationConsultantForm(forms.ModelForm):

    custom_text = forms.CharField(
        label='Custom text',
        required=False,
        widget=forms.Textarea(
            attrs={'placeholder': 'Write a personal text to be added to the invitation'},
        ),
    )

    class Meta:
        model = BulkCreation
        fields = ['file_csv']
