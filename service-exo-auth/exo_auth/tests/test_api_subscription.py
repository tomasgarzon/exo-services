import uuid

from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..models import UserSubscription
from ..jwt_helpers import _build_jwt


class SubscriptionTest(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_user()

    def test_create_subscription(self):
        # PREPARE DATA
        data = {
            'uuid': uuid.uuid4().__str__(),
            'email': faker.email(),
            'subscription': 'conversations.conversations'}
        url = reverse('api:on-subscribe')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            UserSubscription.objects.filter(user_uuid=data['uuid']).count(), 1)
        self.assertEqual(
            UserSubscription.objects.filter(subscription=data['subscription']).count(), 1)

    def test_create_unsubscription(self):
        # PREPARE DATA
        data = {
            'uuid': uuid.uuid4().__str__(),
            'subscription': 'conversations.conversations'}
        UserSubscription.objects.create(
            user_uuid=data['uuid'], subscription=data['subscription'])
        url = reverse('api:on-unsubscribe')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            UserSubscription.objects.filter(user_uuid=data['uuid']).count(), 0)
        self.assertEqual(
            UserSubscription.objects.filter(subscription=data['subscription']).count(), 0)

    def test_list_subscriptors(self):
        # PREPARE DATA
        user_uuid = uuid.uuid4().__str__()
        subscriptors = [
            'conversations.conversations',
            '{}.{}'.format(faker.word(), faker.word())
        ]
        for name in subscriptors:
            UserSubscription.objects.create(
                user_uuid=user_uuid, subscription=name)
        UserSubscription.objects.create(
            user_uuid=uuid.uuid4().__str__(),
            subscription='conversations.conversations')
        url = reverse(
            'api:subscriptors',
            kwargs={'subscription': 'conversations.conversations'})

        # DO ACTION
        token = _build_jwt(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.data), 2)
