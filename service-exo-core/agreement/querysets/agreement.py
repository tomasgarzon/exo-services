from django.db import models
from django.db.models import Q
from ..conf import settings

from utils.descriptors import CustomFilterDescriptorMixin


class AgreementQuerySet(CustomFilterDescriptorMixin, models.QuerySet):

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.AGREEMENT_STATUS,
        }, {
            'field': 'domain',
            'options': settings.AGREEMENT_DOMAIN_CHOICES,
        },
    ]

    def filter_by_recipient(self, recipient):
        return self.filter(recipient=recipient)

    def filter_by_consultant(self):
        return self.filter_by_recipient(settings.AGREEMENT_RECIPIENT_CONSULTANT)

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_domain(self, domain):
        return self.filter(domain=domain)

    def latest_version(self):
        return self.latest('version')
