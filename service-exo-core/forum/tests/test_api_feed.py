from django.conf import settings

from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from circles.models import Circle
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from forum.models import Post
from team.faker_factories import FakeTeamFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from utils.faker_factory import faker


class CirclesApiFeedTest(
        UserTestMixin,
        SuperUserTestMixin,
        APITestCase):

    def setUp(self):
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
            activities=[settings.EXO_ACTIVITY_CH_ACTIVITY_CONSULTING])

        for slug in ['ecosystem', 'trainers']:
            circle = Circle.objects.get(slug=slug)
            circle.add_user(self.consultant.user)

    def add_user_to_team(self, user, team):
        team.add_member(
            user_from=self.super_user,
            email=user.email,
            name=user.short_name,
        )
        assign_perm(settings.PROJECT_PERMS_VIEW_PROJECT, user, team.project)
        assign_perm(settings.TEAM_PERMS_FULL_VIEW_TEAM, user, team)
        team.activate(user=user)

    def test_circle_feed(self):
        # PREPARE DATA
        team = FakeTeamFactory.create()
        participant = FakeUserFactory.create(password='123456', is_active=True)
        self.add_user_to_team(participant, team)
        user = self.consultant.user
        user.is_staff = True
        user.save()

        questions = []
        for i in range(2):
            questions.append(
                Post.objects.create_project_team_post(
                    title=' '.join(faker.words()),
                    user_from=participant,
                    team=team)
            )

        announcements = []
        for i in range(3):
            announcements.append(
                Post.objects.create_announcement_post(
                    user_from=self.super_user,
                    title=' '.join(faker.words()),
                    description=faker.text())
            )

        posts = []
        for i in range(4):
            posts.append(
                Post.objects.create_circle_post(
                    circle=Circle.objects.get(slug='ecosystem'),
                    user_from=self.super_user,
                    title=' '.join(faker.words()),
                    description=faker.text())
            )

        posts.append(
            Post.objects.create_circle_post(
                circle=Circle.objects.get(slug='trainers'),
                user_from=self.consultant.user,
                title=' '.join(faker.words()),
                description=faker.text())
        )

        posts[0].reply(
            user_from=self.consultant.user,
            comment=faker.text())
        announcements[0].reply(
            user_from=self.consultant.user,
            comment=faker.text())
        questions[0].reply(
            user_from=self.consultant.user,
            comment=faker.text())

        url = reverse('api:forum:feed')

        # DO ACTION
        self.client.login(
            username=self.consultant.user.username,
            password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('count'), 10)
