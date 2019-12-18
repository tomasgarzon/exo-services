from django import forms
from django.conf import settings


class ConsultantFilterForm(forms.Form):

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name. email or location',
            'class': 'input form-control',
            'type': 'search',
        }),
    )
    order_by = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def show_description(self):
        description = ''
        if self.is_valid():
            values = []
            ignored_fields = ['order_by']
            for key, value in self.cleaned_data.items():
                if not value or key in ignored_fields:
                    continue
                v = self._pretty_value(key, value)
                values.append(str(v))
            if values:
                description = settings.CORE_PREFIX_FILTER_SUMMARY + ', '.join(values)

        return description

    def json_filter(self):
        values = {}
        for key, value in self.cleaned_data.items():
            if not value:
                continue
            v = self._pretty_value(key, value)
            values[key] = v
        return values

    def _pretty_value(self, key, value):
        field = self.fields.get(key)
        if hasattr(field, 'show_description'):
            v = field.show_description(value)
        else:
            if isinstance(field, forms.MultipleChoiceField):
                v = ', '.join([dict(field.choices)[v1] for v1 in value])
            elif isinstance(field, forms.ModelMultipleChoiceField) or isinstance(value, list):
                v = ', '.join([str(v1) for v1 in value])
            elif isinstance(field, forms.ModelChoiceField):
                v = str(value)
            elif hasattr(field, 'choices'):
                v = dict(field.choices)[value]
            elif isinstance(field, forms.BooleanField):
                v = field.label if value else ''
            else:
                v = value
        return v
