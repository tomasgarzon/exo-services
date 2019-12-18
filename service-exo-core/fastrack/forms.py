from django import forms

from project.forms import ProjectMixinForm
from project.signals_define import project_category_changed_signal

from .models import FastrackSprint


class FastrackSprintForm(ProjectMixinForm):

    class Meta:
        model = FastrackSprint
        fields = [
            'name',
            'start',
            'location',
            'timezone',
            'place_id',
            'template',
            'category',
        ]
        labels = {
            'name': 'Fastrack Sprint name',
            'start': 'Start date',
        }
        widgets = {
            'start': forms.TextInput(attrs={'class': 'form_datetime'}),
            'place_id': forms.HiddenInput(),
        }

    def save(self, commit=True):
        super().save(commit)

        if 'category' in self.changed_data:
            project_category_changed_signal.send(
                sender=self.instance.project_ptr.__class__,
                instance=self.instance.project_ptr)
        return self.instance
