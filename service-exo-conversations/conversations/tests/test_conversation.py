from mock import patch

from django import test

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Conversation
from .test_mixin import ConversationMixin


class ConversationTest(UserTestMixin, ConversationMixin, test.TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()
        self.related_object = self.create_object(self.get_user())

    def test_create_conversation(self):
        # DO ACTION
        user_data = self.generate_fake_user_data(self.user)
        conversation = Conversation.objects.start_conversation(
            self.related_object.uuid, self.user, ' '.join(faker.sentences()), [user_data])

        # ASSERTS
        self.assertIsNotNone(conversation)
        self.assertTrue(conversation.can_write(self.user))
        self.assertEqual(
            Conversation.objects.filter(uuid_related_object=self.related_object.uuid, created_by=self.user).count(),
            1)
        self.assertEqual(
            Conversation.objects.filter(uuid_related_object=self.related_object.uuid).count(),
            1)
        # Pending of refactorizing conversation with opportunities
        # self.assertEqual(len(conversation.followers), 2)

    def test_create_multiple_conversations(self):
        # PREPARE DATA
        users = [self.get_user() for _ in range(4)]

        # DO ACTION
        for user in users:
            user_data = self.generate_fake_user_data(user)
            Conversation.objects.start_conversation(
                self.related_object.uuid, user, ' '.join(faker.sentences()), [user_data])

        # ASSERTS
        self.assertEqual(
            Conversation.objects.filter(uuid_related_object=self.related_object.uuid).count(),
            len(users))
        for user in users:
            self.assertEqual(
                Conversation.objects.filter(
                    uuid_related_object=self.related_object.uuid, created_by=user).count(),
                1)

    @patch('auth_uuid.utils.user_wrapper.UserWrapper')
    def test_delivery_manager_can_respond(self, mock_wrapper):
        # PREPARE DATA
        mock_wrapper.is_delivery_manager.return_value = True
        user_data = self.generate_fake_user_data(self.user)
        conversation = Conversation.objects.start_conversation(
            self.related_object.uuid, self.user, ' '.join(faker.sentences()), [user_data])

        user = self.get_user()
        conversation.add_user(user)
        conversation.add_conversation_user(user)

        # DO ACTION
        conversation.add_message(user, faker.word())

        # ASSERTS
        self.assertTrue(conversation.messages.count(), 2)
