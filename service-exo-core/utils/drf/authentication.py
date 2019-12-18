from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import ugettext as _

from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication as JWTAuthentication


class UsernameAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('HTTP_USERNAME')
        if not username or username != settings.AUTH_SECRET_KEY:
            return None

        user = get_user_model().objects.filter(is_superuser=True).first()
        if not user:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class JSONWebTokenAuthentication(JWTAuthentication):

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        user_uuid = payload.get('uuid')

        if not user_uuid:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user
