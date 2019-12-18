from django import forms

from consultant.models import Consultant
from consultant.helpers import (
    ConsultantChoiceField,
    ConsultantMultipleChoiceField
)

from project.forms import ProjectForm

from ..models import Sprint


class SprintSimpleForm(ProjectForm):

    class Meta:
        model = Sprint
        fields = [
            'name', 'start',
            'agenda',
            'location',
            'timezone',
            'place_id',
            'duration',
            'template',
            'category',
        ]
        labels = {
            'start': 'Start date',
            'name': 'Sprint name',
        }
        placeholders = {
            'agenda': 'http://www.example.com/basic.ics',
        }
        widgets = {
            'start': forms.TextInput(attrs={'class': 'form_datetime'}),
            'place_id': forms.HiddenInput(),
        }


class SprintForm(ProjectForm):

    project_manager = ConsultantChoiceField(
        label='Head Coach',
        queryset=Consultant.objects.all().order_by('user__short_name'),
        widget=forms.Select(attrs={'class': 'select2 step1'}),
    )
    coaches = ConsultantMultipleChoiceField(
        label='ExO Coaches',
        queryset=Consultant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2 step1'}),
    )
    speakers = ConsultantMultipleChoiceField(
        required=False,
        label='Speakers',
        queryset=Consultant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2 step1'}),
    )
    align_trainers = ConsultantMultipleChoiceField(
        label='Instructors',
        required=False,
        queryset=Consultant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2 step1'}),
    )
    disruptors = ConsultantMultipleChoiceField(
        label='Disruptors',
        required=False,
        queryset=Consultant.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2 step1'}),
    )

    class Meta:
        model = Sprint
        fields = [
            'name', 'start', 'project_manager',
            'goals', 'challenges',
        ]
        labels = {
            'name': 'Sprint name',
            'start': 'Start date',
        }
        widgets = {
            'goals': forms.Textarea(attrs={'rows': 4}),
            'challenges': forms.Textarea(attrs={'rows': 4}),
        }
