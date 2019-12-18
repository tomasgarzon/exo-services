from django import forms
from consultant.models import Consultant
from utils.forms.form_placeholder import CustomForm, CustomModelForm

from ..models import Coupon


class CouponSearchListForm(CustomForm):

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input form-control'}),
    )

    class Meta:
        placeholders = {
            'search': 'Search by code or owner',
        }


class CreateCouponForm(CustomModelForm):

    referal_user = forms.CharField(
        required=False,
        label='Referal user email',
        widget=forms.EmailInput(attrs={'class': 'input form-control'}))

    class Meta:
        model = Coupon
        fields = [
            'code', 'comment', 'expiry_date',
            'discount', 'type', 'certification',
            'max_uses', 'fixed_email'
        ]
        placeholders = {
            'expiry_date': '%Y-%m-%d %H:%M:%S'
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_referal_user(self):
        value = self.cleaned_data['referal_user']
        if value and not Consultant.all_objects.filter(user__emailaddress__email=value).exists():
            raise forms.ValidationError('User does not exist')
        return value

    def save(self, commit=True):
        coupon = super().save(commit=False)
        coupon.created_by = self.user
        cleaned_data = self.cleaned_data
        if cleaned_data.get('referal_user'):
            coupon.owner = Consultant.objects.get(
                user__emailaddress__email=cleaned_data.get('referal_user')).user
        coupon.save()


class UpdateCouponForm(CreateCouponForm):
    pass
