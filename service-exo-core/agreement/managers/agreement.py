from django.db import models
from django.conf import settings

from utils.descriptors import CustomFilterDescriptorMixin

from ..querysets.agreement import AgreementQuerySet


class AgreementManager(CustomFilterDescriptorMixin, models.Manager):
    queryset_class = AgreementQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.AGREEMENT_STATUS,
        }, {
            'field': 'domain',
            'options': settings.AGREEMENT_DOMAIN_CHOICES,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def for_consultants(self):
        return self.get_queryset().filter_by_consultant()

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_domain(self, domain):
        return self.get_queryset().filter_by_domain(domain)

    def filter_by_recipient(self, recipient):
        return self.get_queryset().filter_by_recipient(recipient)

    def latest_version(self):
        return self.get_queryset().latest_version()
