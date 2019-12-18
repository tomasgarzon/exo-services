from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel

from files.mixins import UploadedFileMixin
from permissions.models import PermissionManagerMixin

from utils.models import CreatedByMixin
from utils.models.slug_field import AutoSlugCustomManagerField
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

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    slug = AutoSlugCustomManagerField(
        populate_from='title',
        unique=True,
        null=True,
        blank=False,
    )
    tags = models.ManyToManyField('keywords.Keyword')
    _type = models.CharField(
        max_length=1,
        choices=settings.FORUM_POST_CH_TYPE)
    status = models.CharField(
        max_length=1,
        choices=settings.FORUM_CH_POST_STATUS,
        default=settings.FORUM_CH_POST_STATUS_DEFAULT)

    CHOICES_DESCRIPTOR_FIELDS = [
        '_type',
        'status',
    ]
    CHOICES_DESCRIPTOR_FIELDS_CHOICES = [
        settings.FORUM_POST_CH_TYPE,
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
        category_name = ''
        if self.is_q_a_session:
            category_name = '{} - {} - {}'.format(
                self.get__type_display(),
                self.content_object.team.project,
                self.content_object.session.name,
            )
        elif self.content_object:
            category_name = self.content_object.name
        else:
            category_name = self.get__type_display()

        return category_name

    @property
    def circle(self):
        if self.is_circle:
            return self.content_object
        return None

    @property
    def qa_session(self):
        if self.is_q_a_session:
            return self.content_object.session
        return None

    @property
    def team(self):
        if self.is_project:
            return self.content_object
        elif self.is_q_a_session:
            return self.content_object.team
        return None

    @property
    def project(self):
        if self.team:
            return self.team.project
        return None

    @property
    def created_by_role(self):
        return self.created_by.user_title

    @property
    def url(self):
        if self.is_circle or self.is_project or self.is_announcement:
            if self.is_circle:
                circle = self.circle.slug
            elif self.is_project:
                circle = 'participant-questions'
            else:
                circle = 'announcements'
            return settings.FRONTEND_POST_DETAIL_PAGE.format(
                slug=self.slug,
                circle=circle)
        elif self.is_q_a_session:
            return settings.FRONTEND_JOBS_SWARM_SESSION_QUESTION_PAGE.format(
                **{
                    'pk_qa_session': self.content_object.session.pk,
                    'pk': self.pk
                })
        else:
            return ''

    @property
    def url_project(self):
        kwargs = {}
        if self.project is not None:
            kwargs = {
                'project_id': self.project.pk,
                'team_id': self.team.pk,
                'pk': self.pk,
            }
        if self.is_project:
            kwargs['section'] = 'ask-ecosystem'
        elif self.is_q_a_session:
            kwargs['section'] = 'swarm-session'
        else:
            kwargs = None
        if kwargs is not None:
            return settings.FRONTEND_PROJECT_QUESTION_PAGE.format(**kwargs)
        return ''

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
