from django import forms

from utils.forms import CustomModelForm


class ZoomFormMixin(CustomModelForm):

    zoom_id = forms.CharField(
        max_length=256,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['zoom_id'].initial = self.instance.zoom_id
