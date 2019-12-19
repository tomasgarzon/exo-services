from django.db import models
from django.contrib.contenttypes.models import ContentType

from utils.descriptors import CustomFilterDescriptorMixin
from project.models import Project

from ..queryset.post import PostQuerySet
from ..conf import settings


class PostManager(CustomFilterDescriptorMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    queryset_class = PostQuerySet

    FILTER_DESCRIPTORS = [
        {
            'field': 'status',
            'options': settings.FORUM_CH_POST_STATUS,
        },
    ]

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        ).filter_by_status_published()

    def create_category_post(self, user_from, circle, *args, **kwargs):
        circle.check_user_can_post(user_from)
        kwargs['created_by'] = user_from
        return self._create_post(user_from, circle, *args, **kwargs)

    def _create_post(self, user_from, category=None, *args, **kwargs):
        tags = kwargs.pop('tags', [])
        email_notification = kwargs.pop('email_notification', True)
        is_draft = kwargs.pop('is_draft', False)
        if is_draft:
            kwargs['status'] = settings.FORUM_CH_DRAFT

        kwargs['category'] = category

        post = super().create(*args, **kwargs)
        post.tags.add(*tags)
        post.see(user_from, notify=False)
        post.action_create(user_from)

        if email_notification:
            post.send_email_created()
        return post

    def update_post(self, post, *args, **kwargs):
        user_from = kwargs.get('user_from')
        post.can_update_or_remove(user_from)
        post.title = kwargs.get('title')
        post.description = kwargs.get('description')
        post.save()
        post.tags.clear()
        tags = kwargs.get('tags')
        post.tags.add(*tags)
        post.action_update(user_from)
        return post

    def filter_by_category(self, category):
        return self.get_queryset().filter_by_category(category)

    def filter_by_categories(self, categories):
        return self.get_queryset().filter_by_categories(categories)

    def filter_by_user_subscribed(self, user):
        return self.get_queryset().filter_by_user_subscribed(user)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_search(self, search):
        return self.get_queryset().filter_by_search(search)


class AllPostManager(PostManager):
    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
