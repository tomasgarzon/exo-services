from django.conf import settings
from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin

from ..querysets import ParticipantQuerySet


class ParticipantManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = ParticipantQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.EVENT_ROLE_STATUS_CHOICES,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )

    def filter_by_role_name(self, role_name):
        return self.get_queryset().filter_by_role_name(role_name)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_email(self, email):
        return self.get_queryset().filter_by_email(email)
