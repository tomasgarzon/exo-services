from django import forms

from .step_stream import StepStreamFormMixin
from ..models import StepStream


class StepPeriodForm(StepStreamFormMixin):

    class Meta:
        model = StepStream
        fields = ['guidelines']
        widgets = {
            'guidelines': forms.Textarea(attrs={'class': 'dev__markdown', 'rows': 3}),
        }
