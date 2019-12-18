from django.db import models
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist

from model_utils.models import TimeStampedModel

from .conf import settings


class ExOActivity(TimeStampedModel):
    order = models.IntegerField()
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=150,
        choices=settings.EXO_ACTIVITY_CH_EXO_CODE,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['order']
        permissions = settings.EXO_ACTIVITY_EXOACTIVITY_PERMISSIONS

    def __str__(self):
        return self.name

    @property
    def perm(self):
        return Permission.objects.get(codename=self.code)

    def enable(self, user):
        try:
            self.consultants.get(
                consultant_profile=user.consultant.exo_profile,
            ).enable()
        except ObjectDoesNotExist:
            # The user does not WANT TO "activate" all objects related with the Agreement Signed
            pass

    def disable(self, user):
        try:
            self.consultants.get(
                consultant_profile=user.consultant.exo_profile,
            ).disable()
        except ObjectDoesNotExist:
            # The user HAS NOT "activated" all objects related with the Agreement Signed
            pass
