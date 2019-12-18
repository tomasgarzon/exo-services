from django.contrib.auth import get_user_model

from conversations.models import Conversation

from populate.populator.builder import Builder


User = get_user_model()


class ConversationBuilder(Builder):

    def create_object(self):
        conversation = self.create_conversation()
        self.create_users(conversation)
        self.create_messages(conversation)
        return conversation

    def create_conversation(self):
        return Conversation.objects.create(
            created_by=self.data.get('created_by'),
            name=self.data.get('name'),
            uuid_related_object=self.data.get('uuid_related_object'),
            uuid=self.data.get('uuid'),
            icon=self.data.get('icon'),
            _type=self.data.get('_type'))

    def create_users(self, conversation):
        for user in self.data.get('users', []):
            conversation.users.create(
                user=user.get('user'),
                name=user.get('name'),
                short_title=user.get('short_title'),
                profile_picture=user.get('profile_picture'),
                profile_url=user.get('profile_url'))
            conversation.add_user(user['user'])

    def create_messages(self, conversation):
        for message in self.data.get('messages', []):
            new_message = conversation.add_message(
                message.get('created_by'),
                message.get('message'))
            for user_read in message.get('readed', []):
                user = user_read.get('user')
                new_message.mark_as_read(user)
