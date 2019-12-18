import json

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from rest_framework import status

from test_utils.test_case_mixins import SuperUserTestMixin
from django.test import TestCase
from project.tests.test_mixins import TestProjectMixin


class FeedbackResponseTest(
        SuperUserTestMixin,
        TestProjectMixin,
        TestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_create_typeform_feedback_for_user(self):
        sprint, team, _ = self._build_sprint()
        project = sprint.project_ptr
        user = team.team_members.first()
        team_member = team.members.get_by_user(user)

        last_feedback, _ = team_member.get_or_create_feedback_for_step(project.steps.last())
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
                'definition': '',
                'calculated': '',
            },
        }

        url_webhook = reverse('public:webhooks:typeform:generic-typeform-feedback')

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
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_ANSWERED
        )
