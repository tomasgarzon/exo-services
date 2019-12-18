from django import forms


class PartnerListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name',
            'class': 'input form-control',
        }),
    )
    order_by = forms.CharField(
        required=True,
        widget=forms.HiddenInput,
    )
