from django import forms

from ..external_services.wrappers import exolever_wrapper


class CustomerUUIDFieldMixin(forms.ModelForm):
    customer = forms.ChoiceField(
        required=False,
        choices=[('', '- Select Customer -')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_customer_choices()

    def clean_customer(self):
        data = self.cleaned_data['customer']
        return None if not data else data

    def init_customer_choices(self):
        partners = exolever_wrapper.get_customers()
        for partner in partners:
            self.fields.get('customer').choices += [(partner.get('uuid'), partner.get('name'))]


class PartnerUUIDFieldMixin(forms.ModelForm):
    partner = forms.ChoiceField(
        required=False,
        choices=[('', '- Select Partner -')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_partner_choices()

    def clean_partner(self):
        data = self.cleaned_data['partner']
        return None if not data else data

    def init_partner_choices(self):
        partners = exolever_wrapper.get_partners()
        for partner in partners:
            self.fields.get('partner').choices += [(partner.get('uuid'), partner.get('name'))]
