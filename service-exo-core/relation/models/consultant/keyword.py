from django.db import models

from model_utils.models import TimeStampedModel

from ...conf import settings
from ...managers.consultant_keyword import ConsultantKeywordManager


class ConsultantKeyword(
        TimeStampedModel
):
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='keywords',
        on_delete=models.CASCADE,
    )
    keyword = models.ForeignKey(
        'keywords.Keyword',
        related_name='consultants',
        on_delete=models.CASCADE,
    )
    level = models.IntegerField(
        choices=settings.RELATION_KEYWORD_CHOICES,
    )

    objects = ConsultantKeywordManager()

    def __str__(self):
        return '{} - {}: {}'.format(self.consultant, self.keyword, self.get_level_display())
