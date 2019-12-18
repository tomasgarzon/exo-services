from django.urls import reverse
from django.utils import timezone
from django.conf import settings
import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Conversation
from .test_mixin import ConversationMixin, request_mock_account


class ConversationAPITest(
        UserTestMixin,
        ConversationMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_list_conversations(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        users = []
        for _ in range(3):
            user = self.get_user()
            user_data = self.generate_fake_user_data(user)
            conversation = Conversation.objects.start_conversation(
                generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            users.append(user)
            conversation.add_user(self.super_user)
            conversation.add_conversation_user(**self.generate_fake_user_data(self.super_user))

        url = reverse(
            'api:conversations-list',
            kwargs={'related_uuid': generic_object.uuid})

        # DO ACTION as superuser
        self.setup_credentials(self.super_user)
        response = self.client.get(url)

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 3)

        # ASSERT for consultant
        self.setup_credentials(users[0])

        response = self.client.get(url)

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 1)

    @requests_mock.Mocker()
    def test_conversation_messages(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])

        url = reverse(
            'api:conversations-messages',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': conversation.pk})

        self.setup_credentials(user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['user'],
            str(user.uuid))

    @requests_mock.Mocker()
    def test_conversation_messages_1_to_1(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation = Conversation.objects.start_conversation(
            None, user, ' '.join(faker.sentences()), [user_data],
            conversation_type=settings.CONVERSATIONS_CH_USER)
        user2 = self.get_user()
        conversation.add_user(user2)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(user2))

        url = reverse(
            'api:conversations-messages',
            kwargs={
                'pk': conversation.pk})

        self.setup_credentials(user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['user'],
            str(user.uuid))

    @requests_mock.Mocker()
    def test_filter_conversation_messages_1_to_1(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)

        # CONVERSATION
        conversation = Conversation.objects.start_conversation(
            None, user, ' '.join(faker.sentences()), [user_data],
            conversation_type=settings.CONVERSATIONS_CH_USER)
        user2 = self.get_user()
        conversation.add_user(user2)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(user2))

        # OTHER CONVERSATION
        conversation = Conversation.objects.start_conversation(
            None, user, ' '.join(faker.sentences()), [user_data],
            conversation_type=settings.CONVERSATIONS_CH_USER)
        user3 = self.get_user()
        conversation.add_user(user3)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(user3))

        url = reverse('api:conversations-list')

        self.setup_credentials(user)

        # DO ACTION
        response = self.client.get(url, data={'user_to': user2.uuid.__str__()})
        response_all = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(status.is_success(response_all.status_code))
        self.assertEqual(
            len(response.json()), 1)
        self.assertEqual(
            len(response_all.json()), 2)

    @requests_mock.Mocker()
    def test_conversation_between_users(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        user_data = self.generate_fake_user_data(user)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
        timestamp = timezone.now()
        url = reverse(
            'api:conversations-reply',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': conversation.id})
        conversation.add_user(self.super_user)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(self.super_user))

        conversations = [
            user, user, self.super_user, user, self.super_user
        ]

        # DO ACTION
        for user_action in conversations:
            self.setup_credentials(user_action)
            data = {'message': ' '.join(faker.sentences())}
            response = self.client.post(url, data=data)
            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
            self.assertIsNotNone(response.data.get('user'))
            self.assertIsNotNone(response.data.get('message'))
            self.assertIsNotNone(response.data.get('unread'))

        self.assertEqual(
            conversation.messages.count(), len(conversations) + 1)
        self.assertEqual(
            conversation.total_unread(user, timestamp),
            2)
        self.assertEqual(
            conversation.total_unread(self.super_user),
            4)
        timestamp = timezone.now()
        # DO ACTION
        url = reverse(
            'api:conversations-messages',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': conversation.id})
        # ACTION FOR USER
        self.setup_credentials(user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            conversation.total_unread(user),
            0)
        messages = response.data.get('results')
        total_unread = 0
        total_unread_expected = 2
        for msg in messages:
            if msg['unread']:
                total_unread += 1
        self.assertEqual(total_unread, total_unread_expected)

        # ACTION FOR SUPER USER
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            conversation.total_unread(self.super_user),
            0)
        total_unread = 0
        total_unread_expected = 4
        messages = response.data.get('results')
        for msg in messages:
            if msg['unread']:
                total_unread += 1
        self.assertEqual(total_unread, total_unread_expected)

    @requests_mock.Mocker()
    def test_conversation_messages_undefined(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        url = reverse(
            'api:conversations-messages',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': 'undefined'})

        self.setup_credentials(user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @requests_mock.Mocker()
    def test_consultant_mark_as_read_conversation(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
        conversation.add_user(self.super_user)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(self.super_user))
        conversation.add_message(user, ' '.join(faker.sentences()))

        self.setup_credentials(self.super_user)
        url = reverse(
            'api:conversations-mark-as-read',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': conversation.id})
        # DO ACTION
        response = self.client.put(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(conversation.total_unread(self.super_user), 0)

    @requests_mock.Mocker()
    def test_conversation_messages_paginated(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
        conversation.add_conversation_user(
            **self.generate_fake_user_data(self.super_user))
        for _ in range(20):
            conversation.add_message(user, ' '.join(faker.sentences()))
        conversation.mark_as_read(self.super_user)
        for _ in range(10):
            conversation.add_message(user, ' '.join(faker.sentences()))

        url = reverse(
            'api:conversations-messages',
            kwargs={
                'related_uuid': generic_object.uuid,
                'pk': conversation.pk})

        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data['results']), 13)
        _, cursor = response.data['next'].split('?cursor=')

        # DO ACTION
        data = {'cursor': cursor}
        response = self.client.get(url, data=data)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data['results']), 8)
        _, cursor2 = response.data['next'].split('?cursor=')
        self.assertNotEqual(cursor, cursor2)

    @requests_mock.Mocker()
    def test_list_conversations_created_by_you(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation.add_user(self.super_user)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(self.super_user))
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, self.super_user,
            ' '.join(faker.sentences()), [self.generate_fake_user_data(self.super_user)])

        url = reverse(
            'api:conversations-list',
            kwargs={'related_uuid': generic_object.uuid})

        # DO ACTION as superuser
        self.setup_credentials(self.super_user)
        response = self.client.get(url, data={'created_by_you': True})

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 1)

    @requests_mock.Mocker()
    def test_create_conversation_from_service(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        user = self.get_user()
        user_data = self.generate_fake_user_data(user)
        conversation = Conversation.objects.start_conversation(
            generic_object.uuid, user, ' '.join(faker.sentences()), [user_data])
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        conversation.add_user(self.super_user)
        conversation.add_conversation_user(
            **self.generate_fake_user_data(self.super_user))

        url = reverse(
            'api:conversations-create-message',
            kwargs={'related_uuid': generic_object.uuid})
        data = {
            'created_by': user.uuid.__str__(),
            'conversation_created_by': user.uuid.__str__(),
            'message': faker.text()
        }
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            conversation.messages.first().message,
            data['message'])
        self.assertEqual(
            conversation.messages.first().created_by,
            user)
