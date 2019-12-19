from actstream.models import Follow
from django.db.models import QuerySet, Q, Subquery, IntegerField
from django.db.models.functions import Cast

from utils.descriptors import CustomFilterDescriptorMixin
from ..conf import settings


class PostQuerySet(CustomFilterDescriptorMixin, QuerySet):

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def filter_by_category(self, category):
        return self.filter(
            category=category)

    def filter_by_categories(self, categories):
        if not categories:
            return self.none()
        return self.filter(
            category__in=categories)

    def filter_by_status(self, status):
        if type(status) == list:
            q_filter = Q(status__in=status)
        else:
            q_filter = Q(status=status)

        return self.filter(q_filter).distinct()

    def filter_by_search(self, search):
        cond1 = Q(title__icontains=search)
        cond2 = Q(description__icontains=search)
        return self.filter(cond1 | cond2).distinct()

    def filter_by_user_subscribed(self, user):
        query = Follow.objects.following_qs(
            user, self.model
        ).annotate(as_integer=Cast('object_id', IntegerField()))

        return self.filter(
            id__in=Subquery(query.values('as_integer')))
