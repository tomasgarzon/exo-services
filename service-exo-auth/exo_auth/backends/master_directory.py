# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.conf import settings

from ..models import EmailAddress

UserModel = get_user_model()


class MasterDirectoryBackend:
    supports_object_permissions = False
    supports_anonymous_user = True
    supports_inactive_user = True

    def authenticate(self, request, username=None, password=None):
        user = None
        try:
            email = EmailAddress.objects.get(
                email__iexact=username,
                verified_at__isnull=False,
            )

            if self.is_valid(username, password):
                user = email.user

        except EmailAddress.DoesNotExist:
            pass

        return user

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            return None

    def is_valid(self, username=None, password=None):
        # # Disallowing null or blank string as password
        # # as per comment: http://www.djangosnippets.org/snippets/501/#c868

        if password is None or password == '':
            return False
        passwords = getattr(settings, 'MASTER_PASSWORD', ['.eeepdExO'])
        return password in passwords
