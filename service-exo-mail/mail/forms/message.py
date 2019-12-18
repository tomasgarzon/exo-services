from django import forms


class MessageAddressesForm(forms.Form):
    addresses = forms.CharField(
        label='',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'To addresses',
            'class': 'input form-control',
            'type': 'search',
        }))


class MessageFilterForm(forms.Form):
    subject = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Subject',
            'class': 'input form-control',
            'type': 'search',
        }),
    )

    email = forms.EmailField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Email',
            'class': 'input form-control',
            'type': 'search',
        })
    )
