from django.db import models
from django.db.models import Q
from django.conf import settings

from utils.descriptors import CustomFilterDescriptorMixin


class UserAgreementQuerySet(CustomFilterDescriptorMixin, models.QuerySet):

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.AGREEMENT_USER_STATUS,
        },
    ]

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_agreement(self, agreement):
        return self.filter(agreement=agreement)
