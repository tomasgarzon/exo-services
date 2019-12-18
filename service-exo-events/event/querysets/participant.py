from django.conf import settings
from django.db import models

from itertools import chain


class ParticipantQuerySet(models.QuerySet):

    def filter_by_role_name(self, role_name):
        roles = list(map(lambda x: x[0], filter(
            lambda x: x[1] == role_name,
            list(chain.from_iterable([_[1] for _ in settings.EVENT_PARTICIPANT_ROLE_CHOICES.items()]))
        )))
        return self.filter(exo_role__code__in=roles)

    def filter_by_status(self, status):
        return self.filter(status=status)

    def filter_by_email(self, email):
        return self.filter(user_email=email)
