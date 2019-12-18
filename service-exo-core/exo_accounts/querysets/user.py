from django.db import models
from django.apps import apps
from django.contrib.auth import get_user_model

from ..lang import UserLanguageManager


class UserQuerySet(models.QuerySet):

    def get_platform_languages(self, users_email):
        manager = UserLanguageManager(emails=users_email)
        return manager.get_platform_languages()

    def get_by_email(self, email):
        try:
            user = self.get(email=email)
        except get_user_model().DoesNotExist:
            EmailAddress = apps.get_model('exo_accounts', 'EmailAddress')
            user = EmailAddress.objects.get(email=email).user

        return user

    def actives_only(self):
        return self.filter(is_active=True)
