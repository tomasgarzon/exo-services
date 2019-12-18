from django.urls import reverse
from django.core import mail

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from utils.faker_factory import faker

from ..faker_factories import FakeTeamFactory


class SendEmailTeamTest(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.sprint = FakeSprintAutomatedFactory.create()

    def test_email(self):
        team1 = FakeTeamFactory.create(project=self.sprint.project_ptr)
        team2 = FakeTeamFactory.create(project=self.sprint.project_ptr)
        self.client.login(username=self.super_user.username, password='123456')
        user1 = team1.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )
        team2.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )

        url = reverse('api:project:team:send-email', kwargs={'project_id': self.sprint.project_ptr.pk})
        data = {
            'teams[0]id': team1.pk,
            'teams[1]id': team2.pk,
            'subject': faker.word(),
            'message': faker.word(),
        }

        response = self.client.post(url, data=data, format='multipart')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(mail.outbox), 2)
        message = mail.outbox[0]
        self.assertEqual(message.to, [user1.email])
        self.assertEqual(message.from_email, self.super_user.email)
