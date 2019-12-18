from django.urls import reverse
from django.conf import settings

from guardian.shortcuts import assign_perm
from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from team.faker_factories import FakeTeamFactory
from utils.faker_factory import faker


from ..models import Post


class APIAskToEcosystemTest(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def add_user_to_team(self, user, team):
        team.add_member(
            user_from=self.super_user,
            email=user.email,
            name=user.short_name,
        )
        assign_perm(settings.PROJECT_PERMS_VIEW_PROJECT, user, team.project)
        assign_perm(settings.TEAM_PERMS_FULL_VIEW_TEAM, user, team)
        team.activate(user=user)

    def test_get_posts_from_team(self):
        # PREPARE DATA
        team_1 = FakeTeamFactory.create()
        team_2 = FakeTeamFactory.create()
        user_team_1 = self.user
        user_team_2 = FakeUserFactory.create(password='123456', is_active=True)
        self.add_user_to_team(user_team_1, team_1)
        self.add_user_to_team(user_team_2, team_2)
        search = 'tosearch'
        post_A_team_1 = Post.objects.create_project_team_post(
            title='{} {}'.format(' '.join(faker.words()), search),
            user_from=user_team_1,
            team=team_1)
        Post.objects.create_project_team_post(
            title=' '.join(faker.words()),
            user_from=user_team_1,
            team=team_1)
        post_team_2 = Post.objects.create_project_team_post(
            title=' '.join(faker.words()),
            user_from=user_team_2,
            team=team_2)

        url_team_1 = reverse(
            'api:forum:questions-team-list',
            kwargs={'project_pk': team_1.project.pk, 'team_pk': team_1.pk})
        url_team_2 = reverse(
            'api:forum:questions-team-list',
            kwargs={'project_pk': team_2.project.pk, 'team_pk': team_2.pk})

        # DO ACTION
        self.client.login(username=user_team_1.username, password='123456')
        response = self.client.get(url_team_1)
        response_search = self.client.get(url_team_1, data={'search': search})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('count'), 2)
        self.assertTrue(status.is_success(response_search.status_code))
        self.assertEqual(response_search.data.get('count'), 1)
        self.assertEqual(
            post_A_team_1.pk, response_search.data.get('results')[0].get('pk'))
        self.assertEqual(
            post_A_team_1.title, response_search.data.get('results')[0].get('title'))
        self.assertEqual(
            post_A_team_1.description, response.data.get('results')[0].get('description'))

        # DO ACTION
        self.client.login(username=user_team_2.username, password='123456')
        response = self.client.get(url_team_2)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('count'), 1)
        self.assertEqual(post_team_2.pk, response.data.get('results')[0].get('pk'))

    def test_get_posts_from_team_without_perms(self):
        # PREPARE DATA
        team = FakeTeamFactory.create()
        exception = False

        # DO ACTION
        try:
            Post.objects.create_project_team_post(self.user, team)
        except Exception:
            exception = True

        # ASSERTS
        self.assertTrue(exception)

    def test_get_questions_from_participants(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory(
            user__is_active=True,
            user__password='123456',
            activities=[settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING])
        team_a = FakeTeamFactory.create()
        team_b = FakeTeamFactory.create()
        participant_a = FakeUserFactory.create(password='123456', is_active=True)
        participant_b = FakeUserFactory.create(password='123456', is_active=True)
        self.add_user_to_team(participant_a, team_a)
        self.add_user_to_team(participant_b, team_b)
        for i in range(7):
            post = Post.objects.create_project_team_post(
                user_from=participant_a,
                team=team_a,
                title=' '.join(faker.words()),
                description=faker.text())

        for i in range(12):
            Post.objects.create_project_team_post(
                user_from=participant_b,
                team=team_b,
                title=' '.join(faker.words()),
                description=faker.text())
        url = reverse('api:forum:questions-participants-list')
        search = 'tosearch'
        post.title = '{} {}'.format(post.title, search)
        post.save()

        # DO ACTION
        self.client.login(username=consultant.user.username, password='123456')
        response = self.client.get(url)
        response_search = self.client.get(url, data={'search': search})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), 19)
        self.assertTrue(status.is_success(response_search.status_code))
        data = response_search.json()
        self.assertEqual(data.get('count'), 1)
