from django import forms

from dal import autocomplete

from ..models import Resource


class ResourceForm(forms.ModelForm):

    class Meta:
        model = Resource
        exclude = ['created_by', 'order']
        widgets = {
            'tags': autocomplete.ModelSelect2Multiple(
                url='api:learning:tags-autocomplete',
            ),
        }
