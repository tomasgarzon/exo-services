from django import forms


class BulkActionsForm(forms.Form):

    actions = forms.ChoiceField(
        required=False,
        choices=(('', 'Select an action'), ),
        widget=forms.Select(attrs={
            'placeholder': 'Select an action',
            'class': 'select2 form-control',
        }),
    )

    object_list = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'hidden',
        }),
    )

    def __init__(self, queryset, options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['objects'] = forms. ModelMultipleChoiceField(
            queryset=queryset,
        )

        self.fields['actions'].choices += options
