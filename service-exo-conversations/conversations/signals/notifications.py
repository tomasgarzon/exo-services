from django.conf import settings

from utils.notifications import send_notifications

from ..api.serializers.conversation import ConversationSerializer
from ..api.serializers.message import MessageSerializer


Request = type('Request', (object,), {'user': None})


def new_conversation_group_handler(sender, instance, created, *args, **kwargs):
    if not created:
        return
    for conversation_user in instance.users.all():
        user = conversation_user.user
        request = Request()
        request.user = user

        serializer = ConversationSerializer(
            instance,
            context={'request': request})
        data = serializer.data
        data['Type'] = instance._type
        action = settings.CONVERSATIONS_ACTION_NEW_CONVERSATION
        send_notifications(action, user.uuid, data)


def new_message_handler(sender, instance, *args, **kwargs):

    for conversation_user in instance.conversation.users.all():
        user = conversation_user.user
        request = Request()
        request.user = user

        serializer = MessageSerializer(
            instance,
            context={'request': request})
        data = serializer.data
        data['conversation'] = instance.conversation.pk
        data['Type'] = instance.conversation._type
        action = settings.CONVERSATIONS_ACTION_NEW_MESSAGE
        send_notifications(action, user.uuid, data)


def see_message_handler(sender, instance, *args, **kwargs):

    for conversation_user in instance.conversation.users.all():
        user = conversation_user.user
        request = Request()
        request.user = user

        data = {
            'id': instance.id,
            'conversation': instance.conversation.pk,
            'Type': instance.conversation._type,
        }
        action = settings.CONVERSATIONS_ACTION_SEE_MESSAGE
        send_notifications(action, user.uuid, data)
