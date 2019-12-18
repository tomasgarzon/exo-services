from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from ..signals_define import signal_conversation_group_created


class ConversationManager(models.Manager):

    def start_conversation(self, related_uuid, user_from, message, users, name='', conversation_type='O'):
        conversation = self.initialize_conversation(
            name,
            conversation_type, related_uuid, user_from, users)
        conversation.add_message(user_from, message)
        return conversation

    def filter_by_object(self, related_uuid):
        return self.get_queryset().filter(uuid_related_object=related_uuid)

    def initialize_conversation(self, name, conversation_type, related_uuid, user_from, users, **kwargs):
        data = {
            'created_by': user_from,
            'uuid_related_object': related_uuid,
            'name': name,
            '_type': conversation_type,
            'icon': kwargs.get('icon', None)
        }
        if 'uuid' in kwargs:
            data['uuid'] = kwargs['uuid']
        if conversation_type == settings.CONVERSATIONS_CH_USER:
            conversation = self.create(
                **data)
            created = True
        else:
            conversation, created = self.get_or_create(
                **data)
        for user in users:
            conversation.add_conversation_user(**user)
            conversation.add_user(user['user'])
        signal_conversation_group_created.send(
            sender=conversation.__class__,
            instance=conversation,
            created=created)
        return conversation

    def update_conversation(self, conversation, name, icon, users):
        conversation.name = name
        conversation.icon = icon
        conversation.save()
        current_users = set(conversation.users.values_list('user__uuid', flat=True))
        new_users = {user.get('user_uuid') for user in users}
        add_users = new_users - current_users

        for user_uuid in add_users:
            for user in users:
                if user.get('user_uuid') == user_uuid:
                    break
            user_data = user.copy()
            user_uuid = user_data.pop('user_uuid')
            user, _ = get_user_model().objects.get_or_create(uuid=user_uuid)
            user_data['user'] = user
            conversation.add_conversation_user(**user_data)
            conversation.add_user(user)

        remove_users = current_users - new_users
        for user_uuid in remove_users:
            user, _ = get_user_model().objects.get_or_create(uuid=user_uuid)
            conversation.users.filter(user=user).delete()
            conversation.remove_user(user)
