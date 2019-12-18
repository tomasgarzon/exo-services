from django.db import models
from django.conf import settings

from utils.descriptors import CustomFilterDescriptorMixin

from ..models import Agreement
from ..querysets.user_agreement import UserAgreementQuerySet


class UserAgreementManager(CustomFilterDescriptorMixin, models.Manager):
    queryset_class = UserAgreementQuerySet
    use_for_related_fields = True

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.AGREEMENT_USER_STATUS,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_agreement(self, agreement):
        return self.get_queryset().filter_by_agreement(agreement)

    def create_user_agreement(self, recipient_type):
        last_active_agreement = Agreement.objects \
            .filter_by_status_active() \
            .filter_by_recipient(recipient_type) \
            .latest_version()

        return self.create(agreement=last_active_agreement)
