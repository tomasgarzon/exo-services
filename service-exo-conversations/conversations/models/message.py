from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

from model_utils.models import TimeStampedModel
from actstream import action as act_action

from utils.models import CreatedByMixin

from ..signals_define import signal_message_seen
from ..conf import settings


class Message(
        CreatedByMixin,
        TimeStampedModel):

    deleted = models.BooleanField(default=False)
    message = models.TextField()
    conversation = models.ForeignKey(
        'Conversation', related_name='messages',
        on_delete=models.CASCADE)
    files = GenericRelation('files.UploadedFile')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.message[:100])

    def mark_as_read(self, user_from):
        act_action.send(
            user_from,
            verb=settings.CONVERSATIONS_ACTION_SEE,
            action_object=self)
        _, created = self.users.update_or_create(
            user=user_from,
            defaults={'read': True})
        if created and user_from != self.created_by:
            signal_message_seen.send(
                sender=self.__class__,
                instance=self)

    def seen(self, user_from):
        return self.users.filter(user=user_from, read=True).exists()

    def can_upload_files(self, user, raise_exception=True):
        allowed = self.created_by == user
        if not allowed and raise_exception:
            raise ValidationError('user can not upload')
        return allowed

    def can_view_uploaded_file(self, user, raise_exception=True):
        allowed = self.conversation.user_in_conversation(user)
        if not allowed and raise_exception:
            raise ValidationError('user can not view')
        return allowed

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        allowed = self.created_by == user
        if not allowed and raise_exception:
            raise ValidationError('user can not update')
        return allowed

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        allowed = self.created_by == user
        if not allowed and raise_exception:
            raise ValidationError('user can not upload')
        return allowed


class MessageUser(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages',
        on_delete=models.CASCADE)
    message = models.ForeignKey(
        'Message',
        related_name='users',
        on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
