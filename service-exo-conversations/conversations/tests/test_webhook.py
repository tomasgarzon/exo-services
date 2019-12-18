import re
import requests_mock

from django import test
from django.conf import settings

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Conversation
from .test_mixin import ConversationMixin
from ..tasks import WebhookOpportunityFirstMessageTask


class ConversationWebhookTest(
        UserTestMixin,
        ConversationMixin, test.TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()
        self.related_object = self.create_object(self.get_user())

    def test_first_message(self):
        # DO ACTION
        user_data = self.generate_fake_user_data(self.user)
        conversation = Conversation.objects.start_conversation(
            self.related_object.uuid, self.user,
            ' '.join(faker.sentences()), [user_data])
        user = self.get_user()
        conversation.add_user(user)
        conversation.add_conversation_user(user)
        message = conversation.add_message(user, faker.word())

        # ASSERTS
        first_message_for_user = not conversation.messages.filter(
            created_by=message.created_by).exclude(pk=message.pk).exists()
        self.assertTrue(first_message_for_user)

    @requests_mock.Mocker()
    def test_task_webhook_first_message(self, mock_request):
        # DO ACTION
        matcher = re.compile(
            '{}{}api/webhook/first-message/'.format(
                settings.EXOLEVER_HOST,
                settings.SERVICE_OPPORTUNITIES_HOST))
        mock_api_webhook = mock_request.register_uri(
            'POST',
            matcher,
            json={})
        user_data = self.generate_fake_user_data(self.user)
        conversation = Conversation.objects.start_conversation(
            self.related_object.uuid, self.user,
            ' '.join(faker.sentences()), [user_data])
        user = self.get_user()
        conversation.add_user(user)
        conversation.add_conversation_user(user)
        message = conversation.add_message(user, faker.word())

        # ASSERTS
        task = WebhookOpportunityFirstMessageTask().s(
            pk=message.pk).apply()
        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(mock_api_webhook.call_count, 1)
        data = mock_api_webhook.last_request.json()
        self.assertEqual(
            data.get('created_by_uuid'),
            user.uuid.__str__())
        self.assertEqual(
            data.get('other_user_uuid'),
            self.user.uuid.__str__())
        self.assertEqual(
            data.get('message'),
            message.message)
        self.assertEqual(
            data.get('opportunity_uuid'),
            conversation.uuid_related_object.__str__())
