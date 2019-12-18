from django.db import models
from django.conf import settings


class CreatedByMixin(models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_related',
        null=True, blank=True,
    )

    created_by_full_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
