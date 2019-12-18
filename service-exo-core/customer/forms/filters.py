from django import forms


class CustomerListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, industry',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )
