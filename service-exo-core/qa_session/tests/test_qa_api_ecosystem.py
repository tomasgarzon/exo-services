from unittest.mock import patch

from django.test import tag
from django.urls import reverse
from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase, MagicMockMixin
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from utils.dates import string_to_datetime
from utils.faker_factory import faker

from .test_mixins import QASessionTestMixin


@tag('sequencial')
class QASessionAPIEcosystemTest(
        UserTestMixin,
        MagicMockMixin,
        SuperUserTestMixin,
        QASessionTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.initialize_swarms(
            superuser=self.super_user,
            user=self.user)

    def test_qa_detail_fail(self):
        # PREPARE DATA
        query_params = {'pk': self.qa_session_first.pk}
        url = reverse('api:swarms:swarms-ecosystem-detail', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_qa_detail_success(self):
        # PREPARE DATA
        query_params = {'pk': self.qa_session_first.pk}
        url = reverse('api:swarms:swarms-ecosystem-detail', kwargs=query_params)
        adv_user = self.advisors_first[0].consultant.user

        # DO ACTION
        self.client.login(username=self.super_user.username, password='123456')
        response_su = self.client.get(url)

        self.client.login(username=adv_user.username, password='123456')
        response_adv = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_su.status_code, status.HTTP_200_OK)
        data = response_su.json()
        self.assertEqual(data.get('pk'), self.qa_session_first.pk)
        self.assertEqual(data.get('name'), self.qa_session_first.name)
        self.assertEqual(
            string_to_datetime(data.get('startAt')),
            self.qa_session_first.start_at)
        self.assertEqual(
            string_to_datetime(data.get('endAt')),
            self.qa_session_first.end_at)

        self.assertEqual(response_adv.status_code, status.HTTP_200_OK)
        data = response_adv.json()
        self.assertEqual(data.get('pk'), self.qa_session_first.pk)
        self.assertEqual(data.get('name'), self.qa_session_first.name)
        self.assertEqual(
            string_to_datetime(data.get('startAt')),
            self.qa_session_first.start_at)
        self.assertEqual(
            string_to_datetime(data.get('endAt')),
            self.qa_session_first.end_at)

        self.assertEqual(
            len(data.get('advisors')),
            self.qa_session_first.members.count())
        for item in data.get('advisors', None):
            self.assertIsNotNone(item.get('pk'))
            self.assertIsNotNone(item.get('shortName'))
            self.assertIsNotNone(item.get('fullName'))
            self.assertIsNotNone(item.get('slug'))
            self.assertIsNotNone(item.get('profilePictures'))

    @patch('forum.tasks.PostAnswerRatingTask.apply_async')
    def test_do_rating(self, answer_rating_task_mock):
        # PREPARE DATA
        post = self.posts_first_A[0]
        advisor = self.advisors_first[0].consultant.user
        answer = post.reply(advisor, comment=faker.text())
        data = {
            'rating': 4,
            'comment': faker.text()
        }
        url = reverse('api:forum:answer-rating', kwargs={'pk': answer.pk})

        # DO ACTION
        self.client.login(username=advisor.username, password='123456')
        response_fail = self.client.put(url, data=data)
        self.client.login(username=self.user.username, password='123456')
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertEqual(response_fail.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(answer_rating_task_mock.called)
        self.assertEqual(answer_rating_task_mock.call_count, 1)
        self.assertIsNotNone(
            self.get_mock_kwarg(answer_rating_task_mock, 'eta'))

    def test_question_list_fail(self):
        # PREPARE DATA
        query_params = {
            'swarm_id': self.qa_session_first.pk
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-questions-list',
            kwargs=query_params)
        adv_user = self.advisors_second[0].consultant.user

        # DO ACTION
        self.client.login(username=adv_user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_list_success(self):
        # PREPARE DATA
        query_params = {
            'swarm_id': self.qa_session_first.pk
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-questions-list',
            kwargs=query_params)
        adv_user = self.advisors_first[0].consultant.user

        # DO ACTION
        self.client.login(
            username=self.super_user.username, password='123456')
        response_su = self.client.get(url)
        self.client.login(
            username=adv_user.username, password='123456')
        response_adv = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_su.status_code, status.HTTP_200_OK)
        data = response_su.json()
        self.assertEqual(
            data.get('count'),
            len(self.posts_first_A) + len(self.post_first_B)
        )
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('answers') > items[i].get('answers'))
            i += 1

        self.assertEqual(response_adv.status_code, status.HTTP_200_OK)
        data = response_adv.json()
        self.assertEqual(
            data.get('count'),
            len(self.posts_first_A) + len(self.post_first_B)
        )
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('answers') > items[i].get('answers'))
            i += 1

    def test_question_list_ordering(self):
        # PREPARE DATA
        query_params = {
            'swarm_id': self.qa_session_first.pk
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-questions-list',
            kwargs=query_params)
        adv_user = self.advisors_first[0].consultant.user

        # DO ACTION
        self.client.login(
            username=self.super_user.username, password='123456')
        response_su = self.client.get(url, data={'ordering': '-modified'})
        self.client.login(
            username=adv_user.username, password='123456')
        response_adv = self.client.get(url, data={'ordering': '-modified'})

        # ASSERTS
        self.assertEqual(response_su.status_code, status.HTTP_200_OK)
        data = response_su.json()
        self.assertEqual(
            data.get('count'),
            len(self.posts_first_A) + len(self.post_first_B)
        )
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('modified') < items[i].get('modified'))
            i += 1

        self.assertEqual(response_adv.status_code, status.HTTP_200_OK)
        data = response_adv.json()
        self.assertEqual(
            data.get('count'),
            len(self.posts_first_A) + len(self.post_first_B)
        )
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('modified') < items[i].get('modified'))
            i += 1

    def test_question_detail_fail(self):
        # PREPARE DATA
        query_params = {
            'swarm_id': self.qa_session_first.pk,
            'pk': self.post_first_B[0].pk,
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-questions-detail',
            kwargs=query_params)
        adv_user = self.advisors_second[0].consultant.user

        # DO ACTION
        self.client.login(username=adv_user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_question_detail_success(self):
        # PREPARE DATA
        post = self.post_first_B[0]
        query_params = {
            'swarm_id': self.qa_session_first.pk,
            'pk': post.pk,
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-questions-detail',
            kwargs=query_params)
        adv_user = self.advisors_second[0].consultant.user

        # DO ACTION
        self.client.login(
            username=self.super_user.username, password='123456')
        response_su = self.client.get(url)
        self.client.login(
            username=adv_user.username, password='123456')
        response_adv = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_su.status_code, status.HTTP_200_OK)
        data = response_su.json()
        self.assertEqual(data.get('pk'), post.pk)
        self.assertIsNotNone(data.get('canEdit'))
        self.assertIsNotNone(data.get('created'))
        self.assertIsNotNone(data.get('modified'))
        self.assertIsNotNone(data.get('description'))
        self.assertIsNotNone(data.get('answersUnseen'))
        self.assertIsNotNone(data.get('createdBy'))
        self.assertIsNotNone(data.get('tags'))
        self.assertIsNotNone(data.get('uploadedFiles'))

        self.assertEqual(response_adv.status_code, status.HTTP_200_OK)
        self.assertEqual(response_adv.json(), data)

    def test_answer_list_fail(self):
        # PREPARE DATA
        query_params = {
            'swarm_id': self.qa_session_first.pk,
            'question_id': self.post_first_B[0].pk,
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-answers-list',
            kwargs=query_params)

        # DO ACTION
        self.client.login(
            username=self.secondary_user.username,
            password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_list_success(self):
        # PREPARE DATA
        post = self.post_first_B[0]
        query_params = {
            'swarm_id': self.qa_session_first.pk,
            'question_id': post.pk,
        }
        url = reverse(
            'api:swarms:swarms-ecosystem-answers-list',
            kwargs=query_params)
        adv_user = self.advisors_second[0].consultant.user

        # DO ACTION
        self.client.login(
            username=self.super_user.username, password='123456')
        response_su = self.client.get(url)
        self.client.login(
            username=adv_user.username, password='123456')
        response_adv = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_su.status_code, status.HTTP_200_OK)
        data = response_su.json()
        self.assertEqual(data.get('count'), post.answers.count())

        self.assertEqual(response_adv.status_code, status.HTTP_200_OK)
        data = response_adv.json()
        self.assertEqual(data.get('count'), post.answers.count())
