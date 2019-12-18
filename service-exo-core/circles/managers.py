from django.db import models

from .querysets import CircleQuerySet


class CircleManager(models.Manager):
    queryset_class = CircleQuerySet

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        ).filter(removed=False)

    def filter_subscribed(self, user_from):
        return self.get_queryset().filter_subscribed(user_from)

    def filter_not_subscribed(self, user_from):
        return self.get_queryset().filter_not_subscribed(user_from)

    def filter_readable(self, user_from):
        return self.get_queryset().filter_readable(user_from)

    def update_circle(self, circle, *args, **kwargs):
        circle.name = kwargs.get('name')
        circle.description = kwargs.get('description')
        circle.image = kwargs.get('image')
        circle.save()
        circle.tags.clear()
        tags = kwargs.get('tags')
        circle.tags.add(*tags)
        return circle


class CircleAllManager(CircleManager):
    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )
