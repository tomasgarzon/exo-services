from django import forms


class ProjectListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name and client',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )


class ConsultantSearchListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name and role',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )


class StepSearchListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by goal and guidelines',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )
