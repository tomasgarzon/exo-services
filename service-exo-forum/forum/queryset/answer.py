from django.db.models import QuerySet, Q

from utils.descriptors import CustomFilterDescriptorMixin

from ..conf import settings


class AnswerQuerySet(CustomFilterDescriptorMixin, QuerySet):
    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def filter_by_category(self, category):
        return self.filter(
            post__category=category)

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()
