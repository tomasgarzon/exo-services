from django.test import override_settings
from django.conf import settings
from django.urls import reverse

from rest_framework import status
from unittest.mock import patch

from test_utils.test_case_mixins import UserTestMixin
from test_utils import DjangoRestFrameworkTestCase
from circles.models import Circle
from utils.faker_factory import faker


class TestJsonMaxSize(
        UserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    @override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=200)
    @patch('forum.tasks.PostSendEmailCreatedTask.apply_async')
    def test_create_post_circle(self, post_emails_task_mock):
        # PREPARE DATA
        self.circle = Circle.objects.first()
        self.user.hubs.create(hub=self.circle.hub)
        data = {
            'title': ' '.join(faker.words()),
            'description': faker.sentence(nb_words=200),
            '_type': settings.FORUM_CH_CIRCLE,
            'tags': [
                {
                    'name': faker.word() + faker.numerify(),
                },
            ]
        }
        url = reverse('api:circles:circles-create', kwargs={'slug': self.circle.slug})
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
