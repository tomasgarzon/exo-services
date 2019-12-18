from django.urls import reverse
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Conversation, Message
from .test_mixin import ConversationMixin


@override_settings(POPULATOR_MODE=True)
class MessageAPITest(
        UserTestMixin,
        ConversationMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()

    def test_list_user_messages(self):
        # PREPARE DATA
        generic_object = self.create_object(user=self.super_user)

        user = self.get_user()
        user_data = self.generate_fake_user_data(user)

        for _ in range(3):
            Conversation.objects.start_conversation(
                generic_object.uuid,
                user,
                ' '.join(faker.sentences()),
                [user_data]
            )

        url = reverse(
            'api:messages-list',
            kwargs={'related_uuid': user.uuid})

        # DO ACTION
        self.setup_credentials(user)
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(Message.objects.filter(created_by=user).count(), 3)
        self.assertEqual(len(response.data), 3)
