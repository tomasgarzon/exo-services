from django.contrib.auth.backends import ModelBackend
from ..models import EmailAddress


class MultiEmailAuthenticationBackend(ModelBackend):
    """
        Allows to login via email address and password. username
        is interpreted as email address.
    """

    def authenticate(self, request, username=None, password=None):
        user = None
        try:
            email = EmailAddress.objects.get(email__iexact=username,
                                             verified_at__isnull=False)
            if email.user.check_password(password):
                user = email.user

        except EmailAddress.DoesNotExist:
            pass

        return user
