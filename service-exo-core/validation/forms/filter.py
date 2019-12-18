from django import forms


class ValidationSearchListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by description',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )
