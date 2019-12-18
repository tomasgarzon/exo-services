import json

from django.conf import settings
from django.urls import reverse

from rest_framework import status

from test_utils.test_case_mixins import SuperUserTestMixin
from django.test import TestCase
from project.tests.test_mixins import TestProjectMixin

from ..faker_factories import FakeUserMicroLearningFactory, FakeMicroLearningFactory
from ..models.microlearning_average import MicroLearningAverage
from ..models import UserMicroLearning


class MicroLearningResponseTest(
        SuperUserTestMixin,
        TestProjectMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_create_microlearning_response_for_user(self):
        # PREPARE DATA
        sprint, team, _ = self._build_sprint()
        step = sprint.project_ptr.steps.first()
        user = team.team_members.first()
        step_stream = step.streams.get(stream=team.stream)
        user_microlearning = FakeUserMicroLearningFactory.create(
            microlearning__step_stream=step_stream,
            user=user,
            team=team,
        )
        object_id = user_microlearning.pk

        data = {
            'event_type': '',
            'event_id': '',
            'form_response': {
                'hidden': {
                    settings.TYPEFORM_FEEDBACK_WEBHOOK_LABEL_OBJECT_ID: object_id
                },
                'answers': '',
                'token': '',
                'form_id': '',
                'submitted_at': '',
                'definition': '',
                'calculated': {
                    'score': 10
                }
            }}

        url_webhook = reverse(
            'public:webhooks:typeform:microlearning-typeform')

        # DO ACTION
        response = self.client.post(
            url_webhook,
            data=json.dumps(data),
            content_type='application/json')

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_microlearning.refresh_from_db()
        self.assertEqual(user_microlearning.responses[0], data)
        self.assertTrue(user_microlearning.is_done)
        self.assertEqual(user_microlearning.team, team)

    def test_microlearning_avg(self):
        # PREPARE DATA
        sprint, team, _ = self._build_sprint(number_of_members=3)
        step1 = sprint.project_ptr.steps.first()
        step2 = sprint.project_ptr.steps.all()[1]

        step1_stream = step1.streams.get(stream=team.stream)
        step2_stream = step2.streams.get(stream=team.stream)
        step_streams = [
            step1_stream, step2_stream
        ]

        micro_learning1 = FakeMicroLearningFactory.create(
            step_stream=step1_stream)
        micro_learning2 = FakeMicroLearningFactory.create(
            step_stream=step2_stream)
        micro_learnings = [
            micro_learning1, micro_learning2]

        # INPUTS
        scores = [
            # step 1
            [10, 2, 3],
            # step 2
            [1, 3, 5]
        ]

        # OUTPUTS
        # average for each user for all steps
        avg_expected_project_user = [
            int(round(11 / 2.0)), int(round(5 / 2.0)), int(round(8 / 2.0))
        ]
        # average for each step by team
        avg_expected_step_team = [
            5, 3
        ]
        # average for all steps by team
        avg_expected_project_team = [
            int(round(8 / 2.0))
        ]

        scores_others_roles = [
            [2, 10],
            [1, 9]
        ]

        avg_expected_project = [
            int(round(3 / 2.0)),
            int(round(19 / 2.0)),
        ]
        # DO ACTION
        for position, user in enumerate(team.team_members.all()):
            for step_position, step_stream in enumerate(step_streams):
                FakeUserMicroLearningFactory.create(
                    microlearning=micro_learnings[step_position],
                    user=user,
                    score=scores[step_position][position])

        no_team_members = [self.super_user, team.coach.user]
        for position, user in enumerate(no_team_members):
            for step_position, step_stream in enumerate(step_streams):
                FakeUserMicroLearningFactory.create(
                    microlearning=micro_learnings[step_position],
                    user=user,
                    score=scores_others_roles[step_position][position])

        # ASSERTS
        for position, user in enumerate(team.team_members.all()):
            for step_position, step_stream in enumerate(step_streams):
                micro = MicroLearningAverage(
                    step_stream,
                    user,
                    team)
                expected_value = scores[step_position][position]
                user_avg = micro.user_avg
                self.assertEqual(user_avg, expected_value)

                project_user_avg = micro.user_project_avg
                expected_value = avg_expected_project_user[position]
                self.assertEqual(project_user_avg, expected_value)

                team_avg = micro.team_avg
                expected_value = avg_expected_step_team[step_position]
                self.assertEqual(team_avg, expected_value)

                team_project_user_avg = micro.team_project_avg
                expected_value = avg_expected_project_team[0]
                self.assertEqual(team_project_user_avg, expected_value)

        for position, user in enumerate(no_team_members):
            for step_position, step_stream in enumerate(step_streams):
                user_microlearning = UserMicroLearning.objects.get(
                    user=user,
                    microlearning=micro_learnings[step_position])
                micro = MicroLearningAverage(
                    user_microlearning.microlearning.step_stream,
                    user,
                    user_microlearning.team)
                self.assertIsNone(user_microlearning.team)
                expected_value = scores_others_roles[step_position][position]
                user_avg = micro.user_avg
                self.assertEqual(user_avg, expected_value)

                project_user_avg = micro.user_project_avg
                expected_value = avg_expected_project[position]
                self.assertEqual(project_user_avg, expected_value)

                team_avg = micro.team_avg
                self.assertIsNone(team_avg)

                team_project_user_avg = micro.team_project_avg
                self.assertIsNone(team_project_user_avg)
