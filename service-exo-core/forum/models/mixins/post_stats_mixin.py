from actstream import action
from django.utils import timezone

from django.contrib.contenttypes.models import ContentType

from utils.stats import ActionStatsMixin

from ...signals_define import (
    new_action_post,
    new_post_created,
    new_answer_created,
)
from ...conf import settings
from .votes_mixin import VoteMixin


class PostStatsMixin(VoteMixin, ActionStatsMixin):
    _stats_notification = (
        ('see', new_action_post),
        ('create', new_post_created),
        ('reply', new_answer_created),
    )

    def reply(self, user_from, comment, timestamp=None, **kwargs):
        answer = self.answers.filter(
            created_by=user_from,
        ).order_by('created').last()

        data = {
            'verb': settings.FORUM_ACTION_REPLY_POST,
            'action_object': self,
            'target_object': kwargs.get('target_object', None),
        }
        if timestamp:
            data['timestamp'] = timestamp
        action.send(user_from, **data)

        self._notify(
            'reply',
            sender=answer.__class__,
            instance=answer,
            created=True,
            update_fields=None,
            raw=None,
            using=None,
        )

    @property
    def counter_replies(self):
        return self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_REPLY_POST).count()

    def remove_reply(self, answer):
        self.save(update_fields=['modified'])

    def notify_coach(self, user):
        coach = self.team.coach.user
        action.send(
            user,
            verb=settings.FORUM_ACTION_NOTIFY_COACH,
            action_object=self,
            target_object=coach)

    @property
    def coach_notified(self):
        return self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_NOTIFY_COACH).exists()

    def action_create(self, user_from):
        new_post_created.send(
            sender=self.__class__, instance=self,
            created=True,
            update_fields=None, raw=None, using=None,
        )

        action.send(
            user_from,
            verb=settings.FORUM_ACTION_CREATE_POST,
            action_object=self)

    def action_update(self, user_from):
        action.send(
            user_from,
            verb=settings.FORUM_ACTION_EDIT_POST,
            action_object=self)

    def action_removed(self, user_from):
        action.send(
            user_from,
            verb=settings.FORUM_ACTION_REMOVE,
            action_object=self)

    @property
    def new_post_delay(self):
        if self.is_q_a_session:
            return settings.FORUM_NEW_POST_QA_SESSION_DELAY
        return settings.FORUM_NEW_POST_DELAY

    @property
    def edited(self):
        edited = None
        last_edited_action = self.action_object_actions.filter(
            verb=settings.FORUM_ACTION_EDIT_POST).first()

        if last_edited_action:
            edited_after_creating_delay = timezone.now() - last_edited_action.timestamp
            if edited_after_creating_delay.seconds > self.new_post_delay:
                edited = last_edited_action

        return edited

    @property
    def has_been_edited(self):
        return self.edited is not None

    def last_answer_seen(self, user):
        ct = ContentType.objects.get_for_model(user)
        return self.target_actions.filter(
            actor_content_type=ct,
            actor_object_id=user.id,
            verb=settings.STATS_ACTION_GENERIC_SEE).first()

    def new_answers(self, user):
        new_answers = []
        last_see = self.last_answer_seen(user)
        post_answers = self.answers.exclude(created_by=user)
        if not last_see:
            new_answers = post_answers.values_list('pk', flat=True)
        else:
            new_answers = post_answers.filter(
                created__gte=last_see.timestamp).values_list('pk', flat=True)
        return new_answers

    def answers_unseen(self, user):
        ct = ContentType.objects.get_for_model(user)
        answers_seen = self.target_actions.filter(
            verb=settings.STATS_ACTION_GENERIC_SEE,
            actor_content_type=ct,
            actor_object_id=user.id).count()
        answers_total_count = self.answers.count()
        answers_unseen = answers_total_count - answers_seen
        return 0 if answers_unseen < 0 else answers_unseen
