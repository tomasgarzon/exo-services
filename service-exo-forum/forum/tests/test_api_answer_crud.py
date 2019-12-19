from django.urls import reverse
from django.test import tag

from rest_framework import status
from unittest.mock import patch

from circles.tests.mixins import CircleTestMixin
from test_utils import DjangoRestFrameworkTestCase
from test_utils.mock_mixins import MagicMockMixin
from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from sprint.faker_factories import FakeSprintFactory
from team.faker_factories import FakeTeamFactory

from ..models import Post, Answer
from ..conf import settings


class APIAnswerCrudTest(
        MagicMockMixin,
        UserTestMixin,
        CircleTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.init_circles()
        self.create_user()
        self.create_superuser()

    @patch('forum.tasks.PostSendEmailReplyTask.apply_async')
    def test_update_answer_announcement(self, answer_emails_task_mock):
        # PREPARE DATA
        self.user.is_staff = True
        self.user.save()
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )
        answer = post.reply(self.super_user, faker.text())
        url = reverse('api:forum:answer-detail', kwargs={'pk': answer.pk})
        self.client.login(username=self.super_user.username, password='123456')

        # DO ACTION
        data = {'comment': faker.text()}
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        answer.refresh_from_db()
        self.assertEqual(answer.comment, data['comment'])
        self.assertTrue(answer_emails_task_mock.called)
        self.assertEqual(answer_emails_task_mock.call_count, 1)
        self.assertIsNone(
            self.get_mock_kwarg(answer_emails_task_mock, 'eta'))

    @tag('sequencial')
    def test_delete_answer(self):
        # PREPARE DATA
        self.user.is_staff = True
        self.user.save()
        post = Post.objects.create_announcement_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
        )
        answer = post.reply(self.user, faker.text())
        url = reverse('api:forum:answer-detail', kwargs={'pk': answer.pk})
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        data = {'comment': faker.text()}
        response = self.client.delete(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(Answer.objects.filter(pk=answer.pk).exists())
        self.assertTrue(Answer.all_objects.filter(pk=answer.pk).exists())

    @patch('forum.tasks.PostSendEmailReplyTask.apply_async')
    def test_update_answer_team_project(self, answer_emails_task_mock):
        # PREPARE DATA
        sprint = FakeSprintFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_team = FakeTeamFactory.create(project=sprint.project_ptr)
        new_team.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name,
        )
        post = Post.objects.create_project_team_post(
            user_from=self.super_user,
            team=new_team,
            title=' '.join(faker.words()),
            description=faker.text(),
        )
        answer = post.reply(self.user, faker.text())
        url = reverse('api:forum:answer-detail', kwargs={'pk': answer.pk})
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        data = {'comment': faker.text()}
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        answer.refresh_from_db()
        self.assertEqual(answer.comment, data['comment'])
        self.assertTrue(answer_emails_task_mock.called)
        self.assertEqual(answer_emails_task_mock.call_count, 1)
        self.assertIsNotNone(
            self.get_mock_kwarg(answer_emails_task_mock, 'eta'))
