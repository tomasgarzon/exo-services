from django.test import tag
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from exo_accounts.test_mixins import FakeUserFactory
from keywords.faker_factories import FakeKeywordFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from utils.dates import string_to_datetime
from utils.faker_factory import faker

from .test_mixins import QASessionTestMixin


@tag('sequencial')
class QASessionAPITeamTest(
        UserTestMixin,
        SuperUserTestMixin,
        QASessionTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.initialize_swarms(
            superuser=self.super_user,
            user=self.user)

    def test_qa_list_success(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
        }
        url = reverse('api:swarms:swarms-project-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertIsNotNone(item.get('pk'))
            self.assertIsNotNone(item.get('name'))
            self.assertIsNotNone(item.get('startAt'))
            self.assertIsNotNone(item.get('endAt'))

    def test_qa_list_fail(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_B.pk,
        }
        url = reverse('api:swarms:swarms-project-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response_user = self.client.get(url)

        self.client.login(
            username=self.advisors_first[0].consultant.user.username,
            password='123456')
        response_advisor = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_user.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_advisor.status_code, status.HTTP_403_FORBIDDEN)

    def test_qa_detail_success(self):
        # PREPARE DATA
        swarm_id = self.qa_session_first.teams.get(team=self.team_A).pk
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'pk': swarm_id,
        }
        url = reverse('api:swarms:swarms-project-detail', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('pk'), swarm_id)
        self.assertEqual(
            data.get('name'), self.qa_session_first.name)
        self.assertEqual(
            string_to_datetime(data.get('startAt')),
            self.qa_session_first.start_at)
        self.assertEqual(
            string_to_datetime(data.get('endAt')),
            self.qa_session_first.end_at)

    def test_qa_detail_mentions(self):
        # PREPARE DATA
        swarm_id = self.qa_session_first.teams.get(team=self.team_A).pk
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'pk': swarm_id,
        }

        url = reverse('api:swarms:swarms-project-mentions', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 5)  # coach + participant + 4 advisors

    def test_qa_detail_mentions_search(self):
        # PREPARE DATA
        swarm_id = self.qa_session_first.teams.get(team=self.team_A).pk
        advisor = self.advisors_first[1].consultant.user
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'pk': swarm_id,
        }
        url = '{}?search={}'.format(
            reverse('api:swarms:swarms-project-mentions', kwargs=query_params),
            advisor.full_name.lower())

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsNot(len(data), 0)

    def test_question_list_success(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk
        }
        url = reverse('api:swarms:swarms-project-questions-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('count'), len(self.posts_first_A))
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('answers') > items[i].get('answers'))
            i += 1

    def test_question_list_ordering(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk
        }
        url = reverse('api:swarms:swarms-project-questions-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url, data={'ordering': '-modified'})

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('count'), len(self.posts_first_A))
        items = data.get('results')
        i = 1
        while i < len(items):
            self.assertFalse(items[i - 1].get('modified') < items[i].get('modified'))
            i += 1

    def test_question_list_fail(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_B.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
        }
        url = reverse('api:swarms:swarms-project-questions-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.secondary_user.username, password='123456')
        response_user = self.client.get(url)

        self.client.login(
            username=self.advisors_first[0].consultant.user.username,
            password='123456')
        response_advisor = self.client.get(url)

        # ASSERTS
        self.assertEqual(response_user.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_advisor.status_code, status.HTTP_404_NOT_FOUND)

    def test_question_detail_success(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'pk': self.posts_first_A[0].pk
        }
        url = reverse('api:swarms:swarms-project-questions-detail', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data.get('pk'), self.posts_first_A[0].pk)
        self.assertIsNotNone(data.get('canEdit'))
        self.assertIsNotNone(data.get('created'))
        self.assertIsNotNone(data.get('modified'))
        self.assertIsNotNone(data.get('title'))
        self.assertIsNotNone(data.get('description'))
        self.assertIsNotNone(data.get('answersUnseen'))
        self.assertIsNotNone(data.get('createdBy'))
        self.assertIsNotNone(data.get('tags'))
        self.assertIsNotNone(data.get('uploadedFiles'))

    def test_question_detail_mentions(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'pk': self.posts_first_A[0].pk
        }
        url = reverse(
            'api:swarms:swarms-project-questions-mentions', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_answer_list_fail(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'question_id': self.posts_first_A[0].pk
        }

        url = reverse('api:swarms:swarms-project-answers-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.secondary_user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_answer_list_success(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'question_id': self.posts_first_A[0].pk
        }

        url = reverse('api:swarms:swarms-project-answers-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get('count'), self.posts_first_A[0].answers.count())

    def test_question_create_success(self):
        # PREPARE DATA
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
        }
        url = reverse('api:swarms:swarms-project-questions-list', kwargs=query_params)

        keyword = FakeKeywordFactory.create()
        new_post = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                }
            ],
            'uploaded_files': self.get_files_example(2),
        }

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=new_post)

        # ASSERTS
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIsNotNone(data.get('pk', None))
        self.assertEqual(
            data.get('title'), new_post.get('title'))
        self.assertEqual(
            data.get('description'), new_post.get('description'))
        self.assertEqual(
            len(data.get('tags', [])),
            len(new_post.get('tags', [])))
        self.assertEqual(
            len(data.get('uploadedFiles', [])),
            len(new_post.get('uploaded_files', [])))

    def test_question_create_fail(self):
        # PREPARE DATA
        qa_team = self.qa_session_first.teams.get(team=self.team_A)
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': qa_team.pk,
        }
        url = reverse('api:swarms:swarms-project-questions-list', kwargs=query_params)
        keyword = FakeKeywordFactory.create()
        new_post = {
            'title': ' '.join(faker.words()),
            'description': faker.text(),
            'tags': [
                {
                    'pk': keyword.pk,
                    'name': keyword.name,
                },
                {
                    'name': faker.word(),
                },
            ],
            'uploaded_files': self.get_files_example(2),
        }
        new_post_bad_request = new_post
        new_post_bad_request.pop('title')

        # DO ACTION
        self.client.login(
            username=self.secondary_user.username,
            password='123456')
        res_unauth = self.client.post(url, data=new_post)

        self.client.login(
            username=self.user.username,
            password='123456')
        res_bad_req = self.client.post(url, data=new_post_bad_request)

        # ASSERTS
        self.assertEqual(
            res_unauth.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            res_bad_req.status_code, status.HTTP_400_BAD_REQUEST)

    def test_question_update(self):
        # PREPARE DATA
        user = self.posts_first_A[0].created_by
        user_unauth = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password='123456')
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'pk': self.posts_first_A[0].pk
        }
        new_tags = []
        for i in range(6):
            keyword = FakeKeywordFactory.create()
            new_tags.append({
                'pk': keyword.pk,
                'name': keyword.name,
            })
        url = reverse('api:swarms:swarms-project-questions-detail', kwargs=query_params)

        # DO ACTION
        self.client.login(username=user.username, password='123456')
        response = self.client.get(url)
        post = response.data
        payload_data = {
            'title': '{} EDITED'.format(post.get('title')),
            'description': post.get('description'),
            'tags': new_tags,
            'uploaded_files': self.get_files_example(4),
        }
        response = self.client.put(url, data=payload_data)
        self.client.login(username=user_unauth.username, password='123456')
        response_unauth = self.client.put(url, data=payload_data)

        # ASSERTS
        self.assertEqual(response_unauth.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data.get('title'), payload_data.get('title'))
        self.assertEqual(
            data.get('description'), payload_data.get('description'))
        self.assertEqual(
            len(data.get('tags')), len(payload_data.get('tags')))
        self.assertEqual(
            len(data.get('uploadedFiles')), len(payload_data.get('uploaded_files')))

    def test_question_delete(self):
        # PREPARE DATA
        user = self.posts_first_A[0].created_by
        user_unauth = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password='123456')
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'pk': self.posts_first_A[0].pk
        }
        url = reverse('api:swarms:swarms-project-questions-detail', kwargs=query_params)

        # DO ACTION
        self.client.login(username=user_unauth.username, password='123456')
        response_unauth = self.client.delete(url)
        self.client.login(username=user.username, password='123456')
        response = self.client.delete(url)

        # ASSERTS
        self.assertEqual(response_unauth.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_answer_user_titles(self):
        # PREPARE DATA
        post = self.posts_first_A[1]
        participant = post.created_by
        advisor = self.advisors_first[0].consultant.user
        participant.set_password('123456')
        participant.save()
        advisor.set_password('123456')
        advisor.save()
        post.reply(user_from=advisor, comment=faker.text())
        post.reply(user_from=participant, comment=faker.text())
        query_params = {
            'project_id': self.qa_session_first.project.pk,
            'team_id': self.team_A.pk,
            'swarm_id': self.qa_session_first.teams.get(team=self.team_A).pk,
            'question_id': post.pk
        }
        url = reverse('api:swarms:swarms-project-answers-list', kwargs=query_params)

        # DO ACTION
        self.client.login(username=advisor.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        participant_reply = data.get('results')[0]
        adv_reply = data.get('results')[1]
        self.assertEqual(
            adv_reply.get('createdBy').get('userTitle'), advisor.user_title)
        self.assertEqual(adv_reply.get('createdBy').get('projectTitle'), '')
        self.assertIsNone(
            participant_reply.get('createdBy').get('userTitle'))
        self.assertTrue(
            'Participant' in participant_reply.get('createdBy').get('projectTitle'))
