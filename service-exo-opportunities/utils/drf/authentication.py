from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import authentication
from rest_framework import exceptions


class UsernameAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('HTTP_USERNAME')
        if not username or username != settings.AUTH_SECRET_KEY:
            return None

        user = get_user_model().objects.filter(is_superuser=True).first()
        if not user:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
