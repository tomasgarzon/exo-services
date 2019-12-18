from django import forms

from consultant.models import Consultant
from django.conf import settings

from relation.models import ConsultantProjectRole

from .models import QASession


class QASessionForm(forms.ModelForm):

    consultants = forms.ModelMultipleChoiceField(
        label='Advisors',
        queryset=Consultant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
    )

    class Meta:
        model = QASession
        fields = ['start_at', 'end_at', 'consultants', 'name']
        widgets = {
            'start_at': forms.TextInput(attrs={'class': 'form_datetime'}),
            'end_at': forms.TextInput(attrs={'class': 'form_datetime'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)
        self.project = project
        self.fields['consultants'].queryset = ConsultantProjectRole.objects.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_ADVISOR).filter_by_project(project).consultants()

    def clean_start_at(self):
        start = self.cleaned_data.get('start_at')
        if start:
            start = start.replace(tzinfo=None)
            tz = self.project.timezone
            start = tz.localize(start)
        return start

    def clean_end_at(self):
        end = self.cleaned_data.get('end_at')
        if end:
            end = end.replace(tzinfo=None)
            tz = self.project.timezone
            end = tz.localize(end)
        return end

    def clean(self):
        start_at = self.cleaned_data.get('start_at')
        end_at = self.cleaned_data.get('end_at')
        if start_at >= end_at:
            self.add_error('start_at', 'End must be greater than start')
        return self.cleaned_data

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        instance.project = self.project
        instance.save()

        consultants = self.cleaned_data.get('consultants').values_list('id', flat=True)

        consultant_project_roles = ConsultantProjectRole.objects.filter_by_exo_role_code(
            settings.EXO_ROLE_CODE_ADVISOR).filter_by_project(self.project).filter(consultant__id__in=consultants)

        for c_project_role in consultant_project_roles:
            instance.qa_session_advisors.get_or_create(consultant_project_role=c_project_role)

        instance.send_advisor_selected_email()

        return instance
