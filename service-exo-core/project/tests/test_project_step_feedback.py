from django.conf import settings

from faker import Factory as FakerFactory

from exo_role.models import ExORole

from relation.faker_factories import FakeConsultantProjectRoleFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from project.tests.test_mixins import TestProjectMixin
from utils.random import random
from utils.typeform_feedback import build_simple_user_feedback

faker = FakerFactory.create(getattr(settings, 'FAKER_SETTINGS_LOCALE', 'en_GB'))


class ProjectStepFeedbackTest(
        SuperUserTestMixin,
        TestProjectMixin
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_create_generic_typeform_feedback(self):
        sprint = FakeSprintAutomatedFactory()
        self.assertTrue(sprint.steps.exists())
        # There are typeform feedback for each step, except the first one
        for step in sprint.steps.filter(index__gt=1):
            for step_stream in step.streams.all():
                self.assertTrue(step_stream.typeform_feedback.exists())
        # the first step doesn't have feedback
        step = sprint.steps.first()
        for step_stream in step.streams.all():
            self.assertFalse(step_stream.typeform_feedback.exists())

    def test_create_typeform_feedback_for_user(self):
        sprint, team, _ = self._build_sprint()
        project = sprint.project_ptr
        user = team.team_members.first()
        team_member = team.members.get_by_user(user)
        first_feedback, _ = team_member.get_or_create_feedback_for_step(project.steps.first())
        self.assertIsNone(first_feedback)
        last_feedback, _ = team_member.get_or_create_feedback_for_step(project.steps.last())
        self.assertIsNotNone(last_feedback)

    def test_simple_user_feedback(self):
        sprint, team, _ = self._build_sprint()
        project = sprint.project_ptr
        step_stream_first = project.steps.first().streams.get(stream=settings.PROJECT_STREAM_CH_STRATEGY)
        step_stream_last = project.steps.last().streams.get(stream=settings.PROJECT_STREAM_CH_STRATEGY)

        # not team members can't give feedback
        not_participants = [self.super_user, team.coach.user]
        steps = [step_stream_first, step_stream_last]
        for not_participant_user in not_participants:
            for step in steps:
                simple_user_feedback = build_simple_user_feedback(
                    user_from=not_participant_user,
                    step_stream=step,
                )
                self.assertIsNone(simple_user_feedback)

        # team member can give us feedback, except for first one
        participant_user = team.team_members.all().first()

        # first step
        participant_user_feedback = build_simple_user_feedback(
            user_from=participant_user,
            step_stream=step_stream_first,
        )
        self.assertIsNone(participant_user_feedback)

        # last step
        participant_user_feedback = build_simple_user_feedback(
            user_from=participant_user,
            step_stream=step_stream_last,
        )
        self.assertEqual(participant_user_feedback.status, settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_PENDING)

    def test_team_step_do_rating(self):
        # PREPARE TEST
        sprint, team, _ = self._build_sprint()
        pm = FakeConsultantProjectRoleFactory.create(
            project=sprint,
            consultant__user__is_active=True,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )
        pm.activate(self.super_user)
        team_step = team.steps.first()

        participant_user = team.team_members.first()
        coach_user = team.coach.user

        # DO ACTION
        participant_rate = team_step.do_rating(
            participant_user,
            random.randint(0, 5),
            faker.text(),
        )
        coach_rate = team_step.do_rating(
            coach_user,
            random.randint(0, 5),
            faker.text(),
        )

        # DO ASSERTIONS
        self.assertIsNotNone(participant_rate)
        self.assertIsNotNone(coach_rate)
