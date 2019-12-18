from actstream.models import following
from django.conf import settings
from django.db.models import QuerySet, Q


class CircleQuerySet(QuerySet):

    def _get_subscribed_circles_pk(self, user_from):
        return [c.pk for c in following(user_from, self.model)]

    def filter_not_subscribed(self, user_from):
        circle_pks = self._get_subscribed_circles_pk(user_from)
        q_public = ~Q(type=settings.CIRCLES_CH_TYPE_SECRET)
        return self.filter(q_public).exclude(pk__in=circle_pks)

    def filter_subscribed(self, user_from):
        circle_pks = self._get_subscribed_circles_pk(user_from)
        return self.filter(pk__in=circle_pks)

    def filter_readable(self, user_from):
        query = ~Q(type=settings.CIRCLES_CH_TYPE_SECRET)
        query |= Q(
            type=settings.CIRCLES_CH_TYPE_SECRET,
            pk__in=self._get_subscribed_circles_pk(user_from),
        )
        return self.filter(query)
