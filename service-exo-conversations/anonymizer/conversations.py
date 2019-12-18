from dj_anonymizer.register_models import (
    AnonymBase,
    register_anonym,
)
from dj_anonymizer import anonym_field

from utils.faker_factory import faker

from conversations import models


class ConversationAnonym(AnonymBase):
    name = anonym_field.function(faker.sentence)

    class Meta:
        exclude_fields = [
            'actor_actions',
            'action_object_actions',
            'created',
            'created_by',
            'deleted',
            'icon',
            'last_message_timestamp',
            'modified',
            'uuid',
            'uuid_related_object',
            'target_actions',
            '_type',
        ]


class ConversationUserAnonym(AnonymBase):
    name = anonym_field.function(faker.name)
    profile_picture = anonym_field.function(faker.image_url)
    short_title = anonym_field.function(faker.sentence)
    profile_url = anonym_field.function(faker.uri)

    class Meta:
        exclude_fields = [
            'created',
            'modified',
            'user',
            'conversation',
        ]


class MessageAnonym(AnonymBase):
    message = anonym_field.function(faker.text)

    class Meta:
        exclude_fields = [
            'actor_actions',
            'action_object_actions',
            'modified',
            'created',
            'created_by',
            'deleted',
            'conversation',
            'files',
            'target_actions',
        ]


register_anonym([
    (models.Conversation, ConversationAnonym),
    (models.ConversationUser, ConversationUserAnonym),
    (models.Message, MessageAnonym),
])
