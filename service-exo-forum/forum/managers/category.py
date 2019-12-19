from django.db import models

from .querysets.category import CategoryQuerySet


class CategoryManager(models.Manager):
    queryset_class = CategoryQuerySet

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

    def update_category(self, category, *args, **kwargs):
        category.name = kwargs.get('name')
        category.description = kwargs.get('description')
        category.image = kwargs.get('image')
        category.save()
        category.tags.clear()
        tags = kwargs.get('tags')
        category.tags.add(*tags)
        return category


class CategoryAllManager(CategoryManager):
    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )
