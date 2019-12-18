from django import forms
from django.forms import modelformset_factory
from django.conf import settings

from .step_period import StepPeriodForm
from .step_stream import StepStreamForm
from ..models import StepStream, Step


class StepForm(forms.ModelForm):
    name = forms.CharField(required=True)

    class Meta:
        model = Step
        fields = ['name', 'start', 'end']


StepStreamFactory = modelformset_factory(StepStream, form=StepStreamForm, extra=0)
StepPeriodStreamFactory = modelformset_factory(StepStream, form=StepPeriodForm, extra=0)


class StepImportYml(forms.Form):
    streams = forms.MultipleChoiceField(
        required=True,
        choices=settings.PROJECT_STREAM_CH_TYPE)
    file = forms.FileField(required=True)
