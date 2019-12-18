from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from circles.models import Circle
from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..models import Post


from django.contrib.auth import get_user_model


class APIPostCrudTest(
        UserTestMixin, SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        post_id = post.pk
        self.post = Post.objects.get(pk=post_id)

    def test_mention_api_search_in_user_circle(self):
        # PREPARE DATA
        url = reverse('api:mentions:search')
        last_user = get_user_model().objects.last()
        self.circle.add_user(last_user)
        post_data = {
            'search': last_user.full_name,
            'circle_pk': self.circle.pk,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.circle.check_user_can_post(self.user))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('name'), last_user.full_name)
        self.assertTrue(last_user in self.circle.followers)

    def test_mention_api_search_user_not_present_in_circle(self):
        # PREPARE DATA
        url = reverse('api:mentions:search')
        last_user = get_user_model().objects.last()
        post_data = {
            'search': last_user.full_name,
            'circle_pk': self.circle.pk,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.circle.check_user_can_post(self.user))
        self.assertEqual(len(response.data), 0)
        self.assertFalse(last_user in self.circle.followers)

    def test_mention_api_search_in_no_user_circle(self):
        # PREPARE DATA
        circle = Circle.objects.last()
        url = reverse('api:mentions:search')
        last_user = get_user_model().objects.last()
        post_data = {
            'search': last_user.full_name,
            'circle_pk': circle.pk,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertFalse(circle.check_user_can_post(self.user, False))

    def test_mention_api_search_in_not_existing_circle(self):
        # PREPARE DATA
        url = reverse('api:mentions:search')
        last_user = get_user_model().objects.last()
        post_data = {
            'search': last_user.full_name,
            'circle_pk': 999999999,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_mention_api_needs_circle_pk(self):
        # PREPARE DATA
        url = reverse('api:mentions:search')
        last_user = get_user_model().objects.last()
        post_data = {
            'search': last_user.full_name,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_mention_api_search_empty_max_five(self):
        # PREPARE DATA
        url = reverse('api:mentions:search')
        for _ in range(20):
            user = FakeUserFactory.create(
                is_superuser=False,
                is_active=True,
            )
            user.hubs.create(hub=self.circle.hub)

        post_data = {
            'search': '',
            'circle_pk': self.circle.pk,
        }

        # DO ACTIONS
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=post_data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 5)
