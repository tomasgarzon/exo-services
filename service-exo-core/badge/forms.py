from django import forms

from utils.forms.fields import UserEmailAddressField
from utils.forms import CustomModelForm

from .models import Badge, UserBadge, UserBadgeItem
from .conf import settings


class BadgeSearchListForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by user name or email',
            'class': 'input form-control',
        }),
    )


class UserBadgeActivityForm(CustomModelForm, forms.ModelForm):
    email = UserEmailAddressField(required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea)

    CHOICES = settings.BADGE_CODE_COMMUNITY_CHOICES

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['badge'].queryset = Badge.objects.all().filter(
            code__in=dict(self.CHOICES).keys()
        )

    class Meta:
        model = UserBadge
        fields = ['email', 'badge', 'comment']


class UserBadgeJobItemForm(forms.ModelForm):

    class Meta:
        model = UserBadgeItem
        fields = ['name', 'date']
