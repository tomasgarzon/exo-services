import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from project.models import UserProjectRole
from project.faker_factories import FakeProjectFactory
from project.tests.test_mixin import ProjectTestMixin


class FeedbackProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def test_create_typeform_feedback_for_user(self):
        # PREPARE DATA
        team = self.project.teams.first()
        for team in self.project.teams.all():
            UserProjectRole.objects.create_participant(
                project=self.project,
                teams=self.project.teams.all(),
                name=faker.name(),
                email=faker.email())
        user = team.participants.first()
        team_member = team.member_manager.get_by_user(user)
        last_feedback, _ = team_member.get_or_create_feedback_for_step(
            self.project.steps.last())
        ct = ContentType.objects.get_for_model(last_feedback)
        object_id = last_feedback.pk

        data = {
            'event_type': '',
            'event_id': '',
            'form_response': {
                'hidden': {
                    settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_CONTENT_TYPE: ct.id,
                    settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_OBJECT_ID: object_id,
                },
                'answers': '',
                'token': '',
                'form_id': '',
                'submitted_at': '',
                'definition': {},
                'calculated': '',
            },
        }

        url_webhook = reverse('typeform:generic-typeform-feedback')

        response = self.client.post(
            url_webhook,
            data=json.dumps(data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        last_feedback.refresh_from_db()
        self.assertEqual(last_feedback.response, data)
        self.assertEqual(
            last_feedback.status,
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_ANSWERED)
