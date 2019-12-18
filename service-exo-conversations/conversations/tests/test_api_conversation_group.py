import uuid
import redis
import json
import time

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import Conversation
from .test_mixin import ConversationMixin, request_mock_account
from ..signals_define import signal_message_created


class ConversationGroupAPITest(
        UserTestMixin,
        ConversationMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def build_groups(self, user):
        data = {
            'userFrom': user.uuid,
            'groups': [
                {'name': 'Group1', 'users': []},
                {'name': 'Group2', 'users': []},
            ],
            'group_type': settings.CONVERSATIONS_CH_PROJECT,
        }
        users_duplicated = [str(uuid.uuid4())]
        for group in data['groups']:
            for _ in range(5):
                group['users'].append({
                    'user_uuid': str(uuid.uuid4()),
                    'name': faker.name(),
                    'profile_picture': faker.image_url(),
                    'profile_url': faker.uri(),
                    'short_title': faker.word()
                })
            for user_duplicated in users_duplicated:
                group['users'].append({
                    'user_uuid': user_duplicated,
                    'name': faker.name(),
                    'profile_picture': faker.image_url(),
                    'profile_url': faker.uri(),
                    'short_title': faker.word()
                })
        return data

    def build_group_user(self, user):
        data = {
            'userFrom': user.uuid,
            'groups': [
                {'name': 'Group1', 'users': []},
                {'name': 'Group2', 'users': []},
            ],
            'group_type': settings.CONVERSATIONS_CH_USER,
        }
        for group in data['groups']:
            group['users'].append({
                'user_uuid': str(uuid.uuid4()),
                'name': faker.name(),
                'profile_picture': faker.image_url(),
                'profile_url': faker.uri(),
                'short_title': faker.word()
            })
            group['users'].append({
                'user_uuid': str(user.uuid),
                'name': faker.name(),
                'profile_picture': faker.image_url(),
                'profile_url': faker.uri(),
                'short_title': faker.word()
            })
        return data

    def create_conversations(self, user, generic_object):
        data = self.build_groups(user)
        conversations = []
        for group in data['groups']:
            users = []
            for user in group.get('users'):
                user_data = user.copy()
                user_uuid = user_data.pop('user_uuid')
                user, _ = get_user_model().objects.get_or_create(uuid=user_uuid)
                user_data['user'] = user
                users.append(user_data)
            conversation = Conversation.objects.initialize_conversation(
                name=group.get('name'),
                conversation_type=data.get('group_type'),
                related_uuid=str(generic_object.uuid),
                user_from=user,
                users=users,
            )
            conversations.append(conversation)
        return conversations

    @requests_mock.Mocker()
    def test_create_conversation_groups(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        data = self.build_groups(self.super_user)
        url = reverse(
            'api:conversations-create-group',
            kwargs={'related_uuid': generic_object.uuid})

        # DO ACTION as superuser
        self.setup_credentials(self.super_user)
        response = self.client.post(url, data=data)

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        conversations = Conversation.objects.filter_by_object(generic_object.uuid)
        self.assertEqual(conversations.count(), 2)
        self.assertEqual(
            Conversation.objects.filter_by_object(
                generic_object.uuid).filter(_type=settings.CONVERSATIONS_CH_PROJECT).count(),
            2)
        for conversation in conversations:
            self.assertEqual(conversation.total_members, 6)
            self.assertEqual(conversation.users.count(), 6)
            self.assertIsNotNone(conversation.uuid)
            self.assertIsNotNone(conversation.last_message_timestamp)

    @requests_mock.Mocker()
    def test_update_conversation_group(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        groups = self.build_groups(self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        conversation = conversations[0]
        group = groups.get('groups')[0]

        url = reverse(
            'api:conversations-update',
            kwargs={
                'related_uuid': generic_object.uuid,
                'conversation_uuid': conversation.uuid.__str__()})

        users = group.get('users')[1:]
        users.append({
            'user_uuid': str(uuid.uuid4()),
            'name': faker.name(),
            'profile_picture': faker.image_url(),
            'profile_url': faker.uri(),
            'short_title': faker.word()
        })
        data = {
            'name': faker.name(),
            'icon': faker.uri(),
            'users': users
        }

        # DO ACTION
        self.setup_credentials(conversation.created_by)
        response = self.client.put(url, data=data)

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(conversation.users.count(), len(users))
        for user in users:
            self.assertTrue(
                conversation.users.filter(user__uuid=user.get('user_uuid')).exists())

    @requests_mock.Mocker()
    def test_create_conversation_groups_user_type(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        data = self.build_group_user(self.super_user)
        url = reverse('api:conversations-create-group')

        # DO ACTION as superuser
        self.setup_credentials(self.super_user)
        response = self.client.post(url, data=data)

        # ASSERTS for superuser
        self.assertTrue(status.is_success(response.status_code))
        conversations = Conversation.objects.filter(
            _type=settings.CONVERSATIONS_CH_USER)
        self.assertEqual(
            conversations.count(),
            2)
        for conversation in conversations:
            self.assertEqual(conversation.total_members, 2)
            self.assertEqual(conversation.users.count(), 2)
            self.assertIsNotNone(conversation.uuid)
            self.assertIsNotNone(conversation.last_message_timestamp)

    @requests_mock.Mocker()
    def test_create_duplicated_conversation_groups(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        data = self.build_groups(self.super_user)
        url = reverse(
            'api:conversations-create-group',
            kwargs={'related_uuid': generic_object.uuid})

        # DO ACTION as superuser
        self.setup_credentials(self.super_user)
        for _ in range(3):
            response = self.client.post(url, data=data)

            # ASSERTS for superuser
            self.assertTrue(status.is_success(response.status_code))
            conversations = Conversation.objects.filter_by_object(generic_object.uuid)
            self.assertEqual(conversations.count(), 2)
            for conversation in conversations:
                self.assertEqual(conversation.total_members, 6)
                self.assertEqual(conversation.users.count(), 6)

    @requests_mock.Mocker()
    def test_messages_unread(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        user_duplicated = get_user_model().objects.annotate(total=Count('conversations')).filter(total=2).first()
        url = reverse(
            'api:conversations-total-unread',
            kwargs={'related_uuid': generic_object.uuid})

        for conversation in conversations:
            for conv_user in conversation.users.exclude(user=user_duplicated):
                user = conv_user.user
                conversation.add_message(user, ' '.join(faker.sentences()))
                request_mock_account.add_mock(
                    user, is_consultant=False, is_superuser=False)

        # DO ACTION USER DUPLICATED
        self.setup_credentials(user_duplicated)
        response = self.client.get(url)

        #  ASSERTS USER DUPLICATED
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data, 10)  # 5 per group

        # DO ACTION USER IN GROUPS
        for conversation in conversations:
            for conv_user in conversation.users.exclude(user=user_duplicated):
                user = conv_user.user
                self.setup_credentials(user)
                response = self.client.get(url)

                #  ASSERTS USER IN GROUPS
                self.assertTrue(status.is_success(response.status_code))
                self.assertEqual(response.data, 4)  # not 5 because he/she wrote one of them

    @requests_mock.Mocker()
    def test_messages_total(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        user_duplicated = get_user_model().objects.annotate(total=Count('conversations')).filter(total=2).first()
        url = reverse(
            'api:conversations-total',
            kwargs={'related_uuid': generic_object.uuid})

        for conversation in conversations:
            for conv_user in conversation.users.exclude(user=user_duplicated):
                user = conv_user.user
                conversation.add_message(user, ' '.join(faker.sentences()))
                request_mock_account.add_mock(
                    user, is_consultant=False, is_superuser=False)

        # DO ACTION USER DUPLICATED
        self.setup_credentials(user_duplicated)
        response = self.client.get(url)

        #  ASSERTS USER DUPLICATED
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['total'], 10)  # 5 per group
        self.assertEqual(response.data['unread'], 10)  # 5 per group

        # DO ACTION USER IN GROUPS
        for conversation in conversations:
            for conv_user in conversation.users.exclude(user=user_duplicated):
                user = conv_user.user
                self.setup_credentials(user)
                response = self.client.get(url)

                #  ASSERTS USER IN GROUPS
                self.assertTrue(status.is_success(response.status_code))
                self.assertEqual(response.data['unread'], 4)  # not 5 because he/she wrote one of them
                self.assertEqual(response.data['total'], 5)

    @requests_mock.Mocker()
    def test_get_conversations(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        user_duplicated = get_user_model().objects.annotate(total=Count('conversations')).filter(total=2).first()
        url = reverse(
            'api:conversations-list',
            kwargs={'related_uuid': generic_object.uuid})

        for conversation in conversations:
            for conv_user in conversation.users.exclude(user=user_duplicated):
                user = conv_user.user
                conversation.add_message(user, ' '.join(faker.sentences()))
                request_mock_account.add_mock(
                    user, is_consultant=False, is_superuser=False)

        # DO ACTION USER DUPLICATED
        self.setup_credentials(user_duplicated)
        response = self.client.get(url)

        #  ASSERTS USER DUPLICATED
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data), 2)

        for c in response.data:
            self.assertIsNotNone(c['name'])
            self.assertEqual(c['total_unread'], 5)
            self.assertEqual(
                len(c['users']), 6)
            for c_user in c['users']:
                self.assertIsNotNone(c_user['slug'])
                self.assertIsNotNone(c_user['user_title'])

    @requests_mock.Mocker()
    def test_create_group_notifications(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        r = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_AUTH_DB)
        p = r.pubsub()
        p.subscribe('broker{}.{}'.format(
            settings.SERVICE_SHORT_NAME,
            settings.SERVICE_SHORT_NAME))
        time.sleep(1)
        message = p.get_message()  # type subscribe
        generic_object = self.create_object(user=self.super_user)

        # DO ACTIONS
        self.create_conversations(self.super_user, generic_object)

        # ASSERTS
        for k in range(12):
            message = p.get_message()
            self.assertIsNotNone(message)
            self.assertIsNotNone(message.get('data'))
            self.assertEqual(message.get('type'), 'message')
            data = json.loads(message.get('data'))
            self.assertEqual(
                data.get('data').get('action'),
                settings.CONVERSATIONS_ACTION_NEW_CONVERSATION)

    @requests_mock.Mocker()
    def test_message_notifications(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        user = get_user_model().objects.annotate(total=Count('conversations')).filter(total=2).first()
        conversation = conversations[0]
        r = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_AUTH_DB)
        p = r.pubsub()
        p.subscribe('broker{}.{}'.format(
            settings.SERVICE_SHORT_NAME,
            settings.SERVICE_SHORT_NAME))
        time.sleep(1)
        p.get_message()  # type subscribe

        # DO ACTION
        msg = conversation.add_message(user, ' '.join(faker.sentences()))
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        signal_message_created.send(
            sender=msg.__class__,
            instance=msg)

        # ASSERTS
        for k in range(6):
            message = p.get_message()
            self.assertIsNotNone(message)
            self.assertIsNotNone(message.get('data'))
            self.assertEqual(message.get('type'), 'message')
            data = json.loads(message.get('data'))
            self.assertEqual(
                data.get('data').get('action'),
                settings.CONVERSATIONS_ACTION_NEW_MESSAGE)
            uuid = data.get('uuid')
            self.assertTrue(
                conversation.users.filter(user__uuid=uuid).exists())

    @requests_mock.Mocker()
    def test_message_seen_notifications(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        generic_object = self.create_object(user=self.super_user)
        conversations = self.create_conversations(self.super_user, generic_object)
        user = get_user_model().objects.annotate(total=Count('conversations')).filter(total=2).first()
        conversation = conversations[0]

        msg = conversation.add_message(user, ' '.join(faker.sentences()))
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        r = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_AUTH_DB)
        p = r.pubsub()
        p.subscribe('broker{}.{}'.format(
            settings.SERVICE_SHORT_NAME,
            settings.SERVICE_SHORT_NAME))
        time.sleep(1)
        p.get_message()  # type subscribe

        msg.mark_as_read(conversation.users.first().user)

        # ASSERTS
        for k in range(6):
            message = p.get_message()
            self.assertIsNotNone(message)
            self.assertIsNotNone(message.get('data'))
            self.assertEqual(message.get('type'), 'message')
            data = json.loads(message.get('data'))
            self.assertEqual(
                data.get('data').get('action'),
                settings.CONVERSATIONS_ACTION_SEE_MESSAGE)
            uuid = data.get('uuid')
            self.assertTrue(
                conversation.users.filter(user__uuid=uuid).exists())
