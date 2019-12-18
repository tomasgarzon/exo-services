from django.db import models
from django.conf import settings


class HubUserQuerySet(models.QuerySet):

    def exclude_consulting(self):
        return self.exclude(hub___type=settings.EXO_HUB_CH_CONSULTANT)
