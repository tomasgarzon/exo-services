from django import forms
from django.contrib.auth import get_user_model

from .models import ConversationUser


class ConversationUserForm(forms.ModelForm):
    uuid = forms.UUIDField(required=True)

    class Meta:
        model = ConversationUser
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        # We can't assume that kwargs['initial'] exists!
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        if 'instance' in kwargs:
            kwargs['initial'].update({'uuid': kwargs.get('instance').uuid})
        super(ConversationUserForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        instance = super().save(commit=False)
        if not hasattr(instance, 'user') and self.cleaned_data.get('uuid'):
            user, _ = get_user_model().objects.get_or_create(uuid=self.cleaned_data.get('uuid'))
            instance.user = user
        if hasattr(instance, 'user'):
            instance.save()
        return instance
