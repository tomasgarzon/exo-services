from django.db import models

from permissions.models import PermissionManagerMixin

from .conf import settings


class InternalOrganization(PermissionManagerMixin, models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Internal Organizations'
        verbose_name = 'Internal Organization'
        permissions = settings.CUSTOM_AUTH_ALL_PERMISSIONS

    def __str__(self):
        return self.name
