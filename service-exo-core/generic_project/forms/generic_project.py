from django import forms

from project.forms import ProjectMixinForm

from ..models import GenericProject


class GenericProjectForm(ProjectMixinForm):
    class Meta:
        model = GenericProject
        fields = [
            'name',
            'description',
            'start',
            'duration',
            'location',
            'timezone',
            'place_id',
            'template',
            'category',
        ]

        labels = {
            'name': 'Project name',
        }
        widgets = {
            'start': forms.TextInput(attrs={'class': 'form_datetime'}),
            'place_id': forms.HiddenInput(),
        }
