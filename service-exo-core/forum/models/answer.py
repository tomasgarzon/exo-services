from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from model_utils.models import TimeStampedModel
from actstream import action as act_action

from files.mixins import UploadedFileMixin
from permissions.models import PermissionManagerMixin
from permissions.shortcuts import has_team_perms
from ratings.models import Rating
from utils.models import CreatedByMixin
from utils.descriptors import ChoicesDescriptorMixin
from utils.mail import handlers
from utils.dates import increase_date

from ..conf import settings
from ..managers.answer import AnswerManager, AllAnswerManager
from ..signals_define import new_action_answer, signal_post_overall_rating_answer_save
from ..models.mails.answer import PostAnswerRating
from .mixins import AnswerStatsMixin, AnswerMetricMixin


class Answer(
        UploadedFileMixin,
        AnswerMetricMixin,
        AnswerStatsMixin,
        PermissionManagerMixin,
        ChoicesDescriptorMixin,
        CreatedByMixin,
        TimeStampedModel):

    comment = models.TextField()
    post = models.ForeignKey(
        'forum.Post',
        related_name='answers',
        on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        'self',
        related_name='replies',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    ratings = GenericRelation(
        'ratings.OverallRating',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='answers')
    status = models.CharField(
        max_length=1,
        choices=settings.FORUM_CH_POST_STATUS,
        default=settings.FORUM_CH_POST_STATUS_DEFAULT)
    logs = GenericRelation('PostAnswerStatus')
    files = GenericRelation('files.UploadedFile')
    objects = AnswerManager()
    all_objects = AllAnswerManager()

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        ordering = ['-modified']
        permissions = settings.FORUM_PERMS_ANSWER_ALL_PERMISSIONS

    def __str__(self):
        return self.comment

    def can_vote(self, user_from, raise_exceptions=True):
        return self.post.can_vote(user_from, raise_exceptions)

    def can_rate(self, user_from, raise_exceptions=True):
        can_rate = False
        if self.post.qa_session:
            author_is_advisor = self.post.qa_session.members.filter_by_user(self.created_by).exists()
            advisor_in_qa = self.post.qa_session.members.filter_by_user(user_from).exists()
            user_in_team = self.post.content_object.team.team_members.filter(
                pk=user_from.pk).exists()
            allowed_user = advisor_in_qa or user_in_team
            if self.created_by != user_from and allowed_user and author_is_advisor:
                can_rate = True
        elif self.post.is_project:
            author = self.created_by
            user_in_team = user_from in self.post.team.get_granted_users()
            if author != user_from and user_in_team and author.is_consultant:
                can_rate = True
        if not can_rate and raise_exceptions:
            raise PermissionDenied
        return can_rate

    def can_edit(self, user_from, raise_exception=True):
        can_edit = user_from.has_perm(
            settings.FORUM_PERMS_EDIT_ANSWER, self)
        if not can_edit and raise_exception:
            raise PermissionDenied

        return can_edit

    def action_update(self, user_from):
        act_action.send(
            user_from,
            verb=settings.FORUM_ACTION_EDIT_ANSWER,
            action_object=self)

    @property
    def edited(self):
        edited = None
        last_edited_action = self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_ANSWER).first()

        if last_edited_action:
            edited_after_creating_delay = timezone.now() - last_edited_action.timestamp
            if edited_after_creating_delay.seconds > settings.FORUM_NEW_POST_DELAY:
                edited = last_edited_action

        return edited

    def can_view_uploaded_file(self, user, raise_exception=True):
        return self.post.can_see(user, raise_exception)

    def can_upload_files(self, user, raise_exception=True):
        can_upload_files = user.has_perm(settings.FORUM_PERMS_EDIT_ANSWER, self)
        if not can_upload_files and raise_exception:
            raise PermissionDenied

        return can_upload_files

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        return False

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        can_delete_uploaded_file = user.has_perm(settings.FORUM_PERMS_EDIT_ANSWER, self)
        if not can_delete_uploaded_file and raise_exception:
            raise PermissionDenied

        return can_delete_uploaded_file

    @property
    def average_rating(self):
        try:
            return self.ratings.first().rating
        except AttributeError:
            return None

    @property
    def counter_rating(self):
        try:
            return self.ratings.first().ratings.count()
        except AttributeError:
            return 0

    @property
    def ratings_user(self):
        rating = self.ratings.first()
        if not rating:
            return {}
        return dict(rating.ratings.values_list('user_id', 'rating'))

    def do_rating(self, user_from, rating, comment=None):
        from ..tasks import PostAnswerRatingTask

        act_action.send(
            user_from,
            verb=settings.FORUM_ACTION_RATING_POST,
            action_object=self)

        category = settings.RATINGS_ANSWER_ADVISOR
        Rating.update(
            rating_context=self,
            rating_object=self,
            user=user_from,
            rating=rating,
            category=category,
            comment=comment,
        )

        signal_post_overall_rating_answer_save.send(
            sender=self.__class__,
            answer=self)

        new_action_answer.send(
            sender=self.__class__,
            instance=self,
            action=settings.FORUM_ACTION_RATING_POST,
        )

        kwargs = {}
        kwargs['eta'] = increase_date(seconds=settings.FORUM_NEW_POST_DELAY)
        PostAnswerRatingTask().s(
            answer_pk=self.pk,
            rating=rating,
        ).apply_async(**kwargs)

        return rating

    @property
    def created_by_role(self):
        return self.created_by.user_title

    def set_status(self, user_from, new_status):
        self.logs.create(
            user=user_from, status=self.status)
        self.status = new_status
        self.save(update_fields=['modified', 'status'])

    def mark_as_removed(self, user_from):
        self.set_status(
            user_from, settings.FORUM_CH_REMOVED)
        act_action.send(
            user_from,
            verb=settings.FORUM_ACTION_REMOVE,
            action_object=self)

    def notify_answer_rating(self, rating):
        email_name = 'post_answer_rating'
        recipients = [self.created_by.email]
        headers_json = PostAnswerRating(self.post, self, rating).get_data()
        headers = {
            'recipients': recipients,
        }
        headers.update(headers_json)
        handlers.mail_handler.send_mail(email_name, **headers)

    @property
    def can_be_voted(self):
        # Answer can be voted if the person who created
        # it is not part of the team, coach or project head coach
        return not has_team_perms(
            self.post.team,
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            self.created_by,
        )
