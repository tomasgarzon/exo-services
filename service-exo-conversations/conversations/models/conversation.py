from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

import uuid as uuid_sys
from model_utils.models import TimeStampedModel
from actstream.models import followers, Follow
from actstream.actions import follow, unfollow
from actstream import action

from utils.models import CreatedByMixin

from ..managers.conversation import ConversationManager
from ..conf import settings
from ..signals_define import signal_message_created


class Conversation(
        CreatedByMixin,
        TimeStampedModel):
    name = models.CharField(
        max_length=500,
        blank=True, null=True,
        default='')
    deleted = models.BooleanField(default=False)
    icon = models.CharField(
        max_length=200,
        blank=True, null=True,
        default='')
    last_message_timestamp = models.DateTimeField(
        blank=True, null=True,
        auto_now_add=True)
    uuid = models.UUIDField(default=uuid_sys.uuid4)
    uuid_related_object = models.UUIDField(
        default=uuid_sys.uuid4,
        blank=True, null=True)
    _type = models.CharField(
        max_length=1,
        choices=settings.CONVERSATIONS_CH_OPTIONS)

    objects = ConversationManager()

    class Meta:
        ordering = ['-last_message_timestamp']

    def __str__(self):
        return str(self.name)

    @property
    def followers(self):
        return followers(self)

    @property
    def first_user(self):
        return self.followers.first()

    def can_write(self, user_from, raise_exceptions=True):
        user_has_written = user_from in self.followers
        if not user_has_written and raise_exceptions:
            raise Exception('Operation Not allowed')
        return user_has_written

    @property
    def is_opportunity_related(self):
        return self._type == settings.CONVERSATIONS_CH_OPPORTUNITIES

    def update_timestamp(self, now=None):
        if not now:
            now = timezone.now()
        self.last_message_timestamp = now
        self.save(update_fields=['last_message_timestamp'])

    def add_conversation_user(self, user, **kwargs):
        try:
            conversation_user, _ = self.users.get_or_create(
                user=user,
                defaults=kwargs)
        except Exception:
            return self.users.filter(user=user).first()
        return conversation_user

    def add_user(self, user_from):
        follow(user_from, self)

    def remove_user(self, user_from):
        unfollow(user_from, self)

    def add_message(self, user_from, message, now=None):
        self.can_write(user_from)
        new_message = self.messages.create(
            created_by=user_from,
            message=message)
        self.add_user(user_from)
        self.update_timestamp(now)
        new_message.mark_as_read(user_from)
        signal_message_created.send(
            sender=new_message.__class__,
            instance=new_message)
        return new_message

    def last_see_timestamp(self, user):
        ct = ContentType.objects.get_for_model(user)
        last_see_action = self.action_object_actions.filter(
            actor_content_type=ct,
            actor_object_id=str(user.id),
            verb=settings.CONVERSATIONS_ACTION_SEE).first()
        timestamp = None
        if last_see_action:
            timestamp = last_see_action.timestamp
        return timestamp

    def see(self, user_from, timestamp=None):
        action_verb = settings.CONVERSATIONS_ACTION_SEE
        data = {
            'verb': action_verb,
            'action_object': self,
        }
        if timestamp:
            data['timestamp'] = timestamp

        action.send(user_from, **data)

    def total_unread(self, user, timestamp=None):
        if not timestamp:
            timestamp = self.last_see_timestamp(user)
        if not timestamp:
            return self.messages.exclude(created_by=user).count()
        else:
            messages_after_see = self.messages.filter(
                created__gt=timestamp,
            ).exclude(created_by=user)
            return len(list(filter(
                lambda x: not x,
                [message.seen(user) for message in messages_after_see])))

    def mark_as_read(self, user):
        self.see(user)
        messages = self.messages.all()
        for message in messages:
            if message.seen(user):
                break
            message.mark_as_read(user)

    @property
    def total_members(self):
        return Follow.objects.followers_qs(self).count()

    def user_in_conversation(self, user):
        return Follow.objects.followers_qs(self).filter(user=user).exists()
