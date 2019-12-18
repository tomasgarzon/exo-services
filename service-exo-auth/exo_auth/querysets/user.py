from django.db import models
from django.apps import apps
from django.contrib.auth import get_user_model


class UserQuerySet(models.QuerySet):

    def get_by_email(self, email):
        try:
            user = self.get(email=email)
        except get_user_model().DoesNotExist:
            EmailAddress = apps.get_model('exo_auth', 'EmailAddress')
            user = EmailAddress.objects.get(email=email).user
        return user
