from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin

from ..queryset.answer import AnswerQuerySet
from ..conf import settings


class AnswerManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    queryset_class = AnswerQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db).filter_by_status_published()

    def filter_by_category(self, category):
        return self.get_queryset().filter_by_category(category)

    def filter_by_post_type(self, post_type):
        return self.get_queryset().filter_by_post_type(post_type)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)


class AllAnswerManager(AnswerManager):

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
