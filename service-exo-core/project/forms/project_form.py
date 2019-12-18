from django import forms
from django.conf import settings

from utils.forms import CustomModelForm

from ..signals_define import (
    edit_project_start_date, edit_project_duration_date,
    project_status_signal, project_category_changed_signal)
from ..models import Project


class ProjectMixinForm(CustomModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.start:
            self.fields['start'].required = True

    def clean_start(self):
        start = self.cleaned_data.get('start')
        """
        if start:
            start = start.replace(tzinfo=None)
            tz = self.instance.timezone
            start = tz.localize(start)
        """
        return start

    def save(self, commit=True):
        super().save(commit)

        # project's duration has changed
        if 'duration' in self.changed_data:
            edit_project_duration_date.send(
                sender=Project,
                instance=self.instance,
            )

        #  If project has no start date
        if 'start' in self.changed_data:
            edit_project_start_date.send(
                sender=Project,
                instance=self.instance,
            )
            project_status_signal.send(
                sender=Project,
                instance=self.instance
            )
        if 'category' in self.changed_data:
            project_category_changed_signal.send(
                sender=Project,
                instance=self.instance)
        return self.instance


class ProjectForm(ProjectMixinForm):
    agenda = forms.URLField(required=False)


class ProjectTypeForm(forms.Form):
    _type = forms.ChoiceField(
        required=True,
        label='Project Type',
        choices=settings.PROJECT_CH_TYPE_PROJECT,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
