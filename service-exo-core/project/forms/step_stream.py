from django import forms

from ..models import StepStream


class StepStreamFormMixin(forms.ModelForm):

    class Meta:
        model = StepStream
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance.step.project.settings.participant_step_feedback_enabled:
            typeform_feedback, _ = instance.get_or_create_typeform_feedback()
            self.fields['typeform_url'] = forms.URLField(required=False)
            self.fields['typeform_url'].label = 'Feedback survey url'
            self.fields['typeform_url'].initial = typeform_feedback.typeform_url

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.instance.step.project.settings.participant_step_feedback_enabled:
            typeform_feedback, _ = self.instance.get_or_create_typeform_feedback()
            typeform_feedback.set_url(self.cleaned_data.get('typeform_url'))
        return self.instance


class StepStreamForm(StepStreamFormMixin):

    class Meta:
        model = StepStream
        fields = ['goal', 'guidelines']
        widgets = {
            'guidelines': forms.Textarea(attrs={'class': 'dev__markdown', 'rows': 3}),
        }
