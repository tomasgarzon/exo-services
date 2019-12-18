from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel


class UserTagged(
        TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='opps_tagged',
        on_delete=models.CASCADE,
    )
    opportunity = models.ForeignKey(
        'Opportunity', related_name='users_tagged',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return '{} - {}'.format(
            self.user, self.opportunity,
        )

    @property
    def applicant(self):
        return self.opportunity.applicants_info.filter(user=self.user).first()
