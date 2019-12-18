from django import forms

from opportunities.helper import initialize_advisor_request_settings_for_project

from ..conf import settings


class ProjectSettingsForm(forms.Form):
    send_welcome_consultant = forms.BooleanField(
        required=False,
        label='Send invitation to consultants automatically',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    send_welcome_participant = forms.BooleanField(
        required=False,
        label='Send invitation to participants automatically',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    fix_password = forms.CharField(
        required=False,
        label='Default password for participants',
    )
    hide_from_my_jobs = forms.BooleanField(
        required=False,
        label='Hide project in "My Jobs" section (not apply unless the project is for training)',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    participant_step_feedback_enabled = forms.BooleanField(
        required=False,
        label='Enable participant can send daily/weekly feedback',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    participant_step_microlearning_enabled = forms.BooleanField(
        required=False,
        label='Enable participant can send micro learning daily/weekly',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    team_communication_enabled = forms.BooleanField(
        required=False,
        label='Enable Team Communication',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    ask_to_ecosystem_enabled = forms.BooleanField(
        required=False,
        label='Enable Ask to Ecosystem',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    directory_enabled = forms.BooleanField(
        required=False,
        label='Enable Directory',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    advisor_request_enabled = forms.BooleanField(
        required=False,
        label='Enable Advisor Request',
        widget=forms.CheckboxInput(attrs={'class': 'ichecks'}),
    )
    version = forms.ChoiceField(
        required=True,
        label='Project version',
        choices=settings.PROJECT_CH_VERSION,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    template_assignments = forms.ChoiceField(
        required=False,
        label='Template for assignments',
        choices=[('', '- Select template -')] + list(settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    num_tickets_per_team = forms.IntegerField(
        required=False,
        label='Num. tickets available for teams')
    tickets_price = forms.IntegerField(
        required=True,
        label='Price for advisory call')
    tickets_currency = forms.ChoiceField(
        required=True,
        label='Currency for advisory call',
        choices=settings.OPPORTUNITIES_CHOICES_PRICE_CURRENCY,
        widget=forms.Select(attrs={'class': 'form-control select2'}))

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.has_changed():
            project_settings = self.instance.settings
            project_settings.launch['send_welcome_consultant'] = self.cleaned_data.get('send_welcome_consultant')
            project_settings.launch['send_welcome_participant'] = self.cleaned_data.get('send_welcome_participant')
            project_settings.launch['fix_password'] = self.cleaned_data.get('fix_password')
            project_settings.participant_step_feedback_enabled = self.cleaned_data.get(
                'participant_step_feedback_enabled')
            project_settings.participant_step_microlearning_enabled = self.cleaned_data.get(
                'participant_step_microlearning_enabled',
            )
            project_settings.version = self.cleaned_data.get('version')
            project_settings.template_assignments = self.cleaned_data.get('template_assignments', None)
            project_settings.team_communication = self.cleaned_data.get(
                'team_communication_enabled', True)
            project_settings.ask_to_ecosystem = self.cleaned_data.get(
                'ask_to_ecosystem_enabled', True)
            project_settings.directory = self.cleaned_data.get(
                'directory_enabled', True)
            project_settings.advisor_request = self.cleaned_data.get('advisor_request_enabled', False)
            project_settings.hide_from_my_jobs = self.cleaned_data.get(
                'hide_from_my_jobs', False)
            project_settings.save()

            try:
                advisor_request_settings = self.instance.advisor_request_settings
            except AttributeError:
                advisor_request_settings = initialize_advisor_request_settings_for_project(
                    self.instance,
                    self.instance.created_by)
            if 'template_assignments' in self.changed_data:
                self.instance.update_assignments_template(
                    self.cleaned_data.get('template_assignments', None))
            advisor_request_settings.total = self.cleaned_data.get('num_tickets_per_team', 0)
            advisor_request_settings.budgets = [
                {
                    'budget': self.cleaned_data.get('tickets_price', 0),
                    'currency': self.cleaned_data.get('tickets_currency', 'D')
                }
            ]
            advisor_request_settings.save()
        return self.instance
