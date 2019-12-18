from django import forms

from utils.forms import CustomModelForm

from project.signals_define import project_category_changed_signal

from ..models import SprintAutomated
from ..conf import settings


class SprintAutomatedSimpleForm(CustomModelForm):
    accomplish = forms.ChoiceField(
        label='What do you want to accomplish?',
        required=True,
        choices=settings.SPRINT_AUTOMATED_CH_ACCOMPLISH,
    )

    transform = forms.ChoiceField(
        label='What are you trying to transform?',
        required=True,
        choices=settings.SPRINT_AUTOMATED_CH_TRANSFORM,
    )

    playground = forms.ChoiceField(
        label='What is your playground?',
        required=True,
        choices=settings.SPRINT_AUTOMATED_CH_PLAYGROUND,
    )

    class Meta:
        model = SprintAutomated
        fields = [
            'name',
            'description',
            'accomplish',
            'transform',
            'playground',
            'location',
            'timezone',
            'place_id',
            'template',
            'category',
        ]

        labels = {
            'name': 'Sprint name',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'place_id': forms.HiddenInput(),
        }

    def save(self, commit=True):
        super().save(commit)

        if 'category' in self.changed_data:
            project_category_changed_signal.send(
                sender=self.instance.project_ptr.__class__,
                instance=self.instance.project_ptr)
        return self.instance
