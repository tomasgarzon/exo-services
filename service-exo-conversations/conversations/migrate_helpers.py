from django.contrib.auth import get_user_model

User = get_user_model()


def migrate_conversation_messages(conversation, messages):
    #  Remove previous messages
    for msg in conversation.messages.all():
        msg.delete()

    for message in messages:
        created_by, _ = User.objects.get_or_create(
            uuid=message.get('user'))
        new_message = conversation.add_message(
            created_by, message.get('message'))
        conversation.messages.filter(pk=new_message.pk).update(
            created=message.get('created'))
        for user_seen in message.get('seen'):
            if user_seen.get('seen'):
                new_message.mark_as_read(
                    User.objects.get_or_create(
                        uuid=message.get('user'))[0])
