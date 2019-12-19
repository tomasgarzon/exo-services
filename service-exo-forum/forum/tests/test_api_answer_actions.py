from django.urls import reverse
from django.test import tag

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from circles.models import Circle
from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from ..models import Post


@tag('sequencial')
class APIAnswerStatTest(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

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
        user = FakeUserFactory.create(is_active=True, password='123456')
        self.circle.add_user(user)
        self.answer = self.post.reply(user, faker.text())

    def test_do_rating(self):
        # PREPARE DATA
        data = {
            'rating': 4,
            'comment': faker.text()
        }
        url = reverse('api:forum:answer-rating', kwargs={'pk': self.answer.pk})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_answer_like_unlike_success(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456')
        self.circle.add_user(consultant.user)
        answer = self.post.reply(consultant.user, faker.text())
        url = reverse('api:forum:answer-like', kwargs={'pk': answer.pk})
        url_unlike = reverse('api:forum:answer-unlike', kwargs={'pk': answer.pk})

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        self.client.put(url)
        response_self_like = self.client.put(url)
        self.client.login(username=consultant.user.username, password='123456')
        response_other_like = self.client.put(url)
        self.client.put(url_unlike)
        response_unlike = self.client.put(url_unlike)

        # ASSERTS
        self.assertTrue(status.is_success(response_self_like.status_code))
        data = response_self_like.json()
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('numLikes'), 1)

        self.assertTrue(status.is_success(response_other_like.status_code))
        data = response_other_like.json()
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('numLikes'), 2)

        self.assertTrue(status.is_success(response_unlike.status_code))
        data = response_unlike.json()
        self.assertFalse(data.get('liked'))
        self.assertEqual(data.get('numLikes'), 1)

    def test_post_like_unlike_not_allowed(self):
        # PREPARE DATA
        url = reverse('api:forum:post-like', kwargs={'pk': self.answer.pk})
        url_unlike = reverse('api:forum:post-unlike', kwargs={'pk': self.answer.pk})
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response_like = self.client.put(url)
        response_unlike = self.client.put(url_unlike)

        # ASSERTS
        self.assertTrue(status.is_client_error(response_like.status_code))
        self.assertTrue(status.is_client_error(response_unlike.status_code))
