import uuid

from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import authentication


class UsernameAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('HTTP_USERNAME')
        if not username or username != settings.AUTH_SECRET_KEY:
            return None

        user = get_user_model().objects.filter(is_superuser=True).first()
        if not user:
            user = get_user_model().objects.create(
                uuid=uuid.uuid4(),
                is_active=True,
                is_superuser=True,
                is_staff=True
            )

        return (user, None)
