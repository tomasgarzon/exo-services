from django.conf import settings
from django.db import models


class ConsultantExOActivityQuerySet(models.QuerySet):

    def disabled_or_pending(self):
        return self.filter(status__in=[
            settings.RELATION_ACTIVITY_STATUS_CH_DISABLED,
            settings.RELATION_ACTIVITY_STATUS_CH_PENDING,
        ])

    def actives(self):
        return self.filter(status=settings.RELATION_ACTIVITY_STATUS_CH_ACTIVE)

    def disabled(self):
        return self.filter(status=settings.RELATION_ACTIVITY_STATUS_CH_DISABLED)

    def pending(self):
        return self.filter(status=settings.RELATION_ACTIVITY_STATUS_CH_PENDING)

    def filter_by_consultant(self, consultant):
        return self.filter(consultant_profile__consultant=consultant)
