from django import forms

from consultant.helpers import (
    ConsultantChoiceField,
)
from consultant.models import Consultant
from zoom_project.forms import ZoomFormMixin

from ..models import Team


class TeamSearchListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name and stream',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )


class TeamFormMixin(ZoomFormMixin):
    coach = ConsultantChoiceField(
        required=True,
        label='ExO Coach',
        queryset=Consultant.objects.all(),
    )

    class Meta:
        model = Team
        fields = ['name', 'stream', 'coach']
        placeholders = {
            'zoom_id': 'XXX-XXX-XXX or XXXXXXXXX',
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coach_widget = {
            'class': 'select2 step1'
        }
        stream_widget = {
            'class': 'select2 step0',
            'data-minimum-results-for-search': 'Infinity',
        }
        self.fields['coach'].queryset = project.consultants_roles.get_team_manager_consultants(project).consultants()
        self.fields['coach'].label = project.team_manager_label
        self.fields['coach'].widget.attrs = coach_widget
        self.fields['stream'].widget.attrs = stream_widget


class TeamForm(TeamFormMixin):

    class Meta:
        model = Team
        fields = ['name', 'stream', 'coach']


class TeamSprintAutomatedForm(TeamFormMixin):
    pass


class TeamGenericProjectForm(TeamFormMixin):

    class Meta:
        model = Team
        fields = ['name', 'stream', 'coach']
