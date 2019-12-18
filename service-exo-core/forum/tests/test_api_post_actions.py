from django.urls import reverse
from django.test import tag

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from test_utils import DjangoRestFrameworkTestCase
from circles.models import Circle
from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from ..models import Post


@tag('sequencial')
class APIPostStatTest(
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

    def test_add_file_to_post(self):
        # PREPARE DATA
        url = reverse('api:file-versioned:add', kwargs={
            'class_name': 'post',
            'object_id': self.post.id
        })
        data = {
            'filestack_status': 'Stored',
            'filename': 'details.png',
            'mimetype': 'image/png',
            'url': 'https://cdn.filestackcontent.com/2loaCC2xTOSXFwbEjPoO'
        }

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_post_like_unlike_success(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456')
        self.circle.add_user(consultant.user)
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        url = reverse('api:forum:post-like', kwargs={'pk': post.pk})
        url_unlike = reverse('api:forum:post-unlike', kwargs={'pk': post.pk})

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
        post = Post.objects.create_circle_post(
            user_from=self.user,
            circle=self.circle,
            title=' '.join(faker.words()),
            description=faker.text())
        url = reverse('api:forum:post-like', kwargs={'pk': post.pk})
        url_unlike = reverse('api:forum:post-unlike', kwargs={'pk': post.pk})
        consultant = FakeConsultantFactory.create(
            user__is_active=True, user__password='123456')

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response_like = self.client.put(url)
        response_unlike = self.client.put(url_unlike)

        # ASSERTS
        self.assertTrue(status.is_client_error(response_like.status_code))
        self.assertTrue(status.is_client_error(response_unlike.status_code))
