from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel
from django_extensions.db.fields import AutoSlugField
from files.mixins import UploadedFileMixin

from utils.models import CreatedByMixin
from utils.permissions import PermissionManagerMixin
from utils.descriptors import ChoicesDescriptorMixin

from ..managers.post import PostManager, AllPostManager
from ..conf import settings
from .mails.mails import PostEmailMixin
from .mixins import PostStatsMixin, PostPermissionsMixin, PostMetricMixin


class Post(
        PostPermissionsMixin,
        PostMetricMixin,
        PostStatsMixin,
        UploadedFileMixin,
        PermissionManagerMixin,
        CreatedByMixin,
        ChoicesDescriptorMixin,
        PostEmailMixin,
        TimeStampedModel):

    # Define here because of AutoSlugField
    objects = PostManager()
    all_objects = AllPostManager()

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        'Category',
        related_name='posts')

    slug = AutoSlugField(
        populate_from='title',
        unique=True,
        null=True,
        blank=False,
    )
    tags = models.ManyToManyField('keywords.Keyword')
    status = models.CharField(
        max_length=1,
        choices=settings.FORUM_CH_POST_STATUS,
        default=settings.FORUM_CH_POST_STATUS_DEFAULT)

    CHOICES_DESCRIPTOR_FIELDS = [
        'status',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.FORUM_CH_POST_STATUS,
    ]

    logs = GenericRelation('PostAnswerStatus')
    files = GenericRelation('files.UploadedFile')

    objects = PostManager()
    all_objects = AllPostManager()
    slug_manager = AllPostManager()

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-modified']
        base_manager_name = 'objects'
        permissions = settings.FORUM_PERMS_POST_ALL_PERMISSIONS

    def __str__(self):
        return self.title

    @property
    def category_name(self):
        return self.category.name

    @property
    def url(self):
        return settings.FORUM_FRONTEND_POST_DETAIL_PAGE.format(
            slug=self.slug,
            category=self.categoy_name)


    def set_status(self, user_from, new_status):
        self.logs.create(
            user=user_from, status=self.status)
        self.status = new_status
        self.save(update_fields=['modified', 'status'])

    def mark_as_removed(self, user_from):
        self.can_update_or_remove(user_from)
        self.set_status(user_from, settings.FORUM_CH_REMOVED)
        self.action_removed(user_from)

    def reply(self, user_from, comment, timestamp=None, **kwargs):
        self.can_reply(user_from)
        answer = self.answers.create(
            comment=comment,
            created_by=user_from,
            reply_to=kwargs.get('reply_to'),
        )
        kwargs['target_object'] = answer
        if timestamp:
            self.answers.filter(pk=answer.pk).update(
                created=timestamp,
                modified=timestamp)
            Post.objects.filter(pk=self.pk).update(modified=timestamp)
        else:
            self.save(update_fields=['modified'])

        if kwargs.get('email_notification', True):
            self.send_email_reply(answer)

        answer.see(user_from)
        super().reply(user_from, comment, timestamp, **kwargs)
        return answer
