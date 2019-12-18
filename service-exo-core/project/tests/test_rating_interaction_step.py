from django import test
from django.test import tag
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from exo_role.models import ExORole

from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from test_utils.redis_test_case_mixin import RedisTestCaseMixin
from utils.faker_factory import faker
from ratings.models import Interaction
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory


@tag('sequencial')
class InteractionStepRatingTestCase(
        UserTestMixin,
        SuperUserTestMixin,
        RedisTestCaseMixin,
        test.TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        self.team = FakeTeamFactory.create(
            coach=FakeConsultantFactory.create(
                user=self.user,
                status=settings.CONSULTANT_STATUS_CH_ACTIVE,
            ),
            project=self.sprint.project_ptr,
        )
        for k in range(3):
            self.team.add_member(
                self.super_user,
                email=faker.email(),
                name=faker.name())
        self.project = self.sprint.project_ptr
        self.head_role = FakeConsultantProjectRoleFactory.create(
            project=self.project,
            consultant=FakeConsultantFactory(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        self.coach_role = self.project.consultants_roles.get(
            consultant=self.team.coach)

    def test_rating_several_team_member_same_step(self):
        # PREPARE DATA
        ratings = [1, 2, 4]
        expected_rating = sum(ratings) / 3.0
        step = self.project.steps.all().first()
        team_step = self.team.steps.get(step=step)

        # DO ACTION
        for index, member in enumerate(self.team.team_members.all()):
            team_step.do_rating(
                member, ratings[index], faker.text(),
            )

        # ASSERTS
        consultant = self.team.coach
        interaction = Interaction.objects.filter(
            user=consultant.user,
            object_id=self.coach_role.id,
            content_type=ContentType.objects.get_for_model(self.coach_role)).first()
        self.assertIsNotNone(interaction)
        self.assertEqual(
            round(interaction.rating, 1),
            round(expected_rating, 1)
        )

        for index, member in enumerate(self.team.team_members.all()):
            self.assertEqual(
                team_step.get_rating_for_user(member),
                ratings[index])

    def test_rating_several_team_member_several_steps(self):
        # PREPARE DATA
        ratings = [
            [1, 2, 2],
            [2, 2, 2],
            [3, 3, 2],
            [3, 2, 1],
        ]

        # DO ACTION
        for index_step in range(4):
            step = self.project.steps.all()[index_step]
            team_step = self.team.steps.get(step=step)

            for index, member in enumerate(self.team.team_members.all()):
                team_step.do_rating(
                    member, ratings[index_step][index], faker.text(),
                )

        expected_rating = sum(map(sum, ratings)) / 12.0

        # ASSERTS
        consultant = self.team.coach
        interaction = Interaction.objects.filter(
            user=consultant.user,
            object_id=self.coach_role.id,
            content_type=ContentType.objects.get_for_model(self.coach_role))
        self.assertEqual(interaction.count(), 1)
        interaction = interaction.first()
        self.assertEqual(
            round(interaction.rating, 1),
            round(expected_rating, 1)
        )
        self.assertEqual(
            interaction.ratings.all().count(),
            4)
        self.assertEqual(
            round(self.coach_role.rating, 1),
            round(expected_rating, 1))

    def test_rating_several_coach_same_step(self):
        # PREPARE DATA
        for k in range(3):
            coach = FakeConsultantFactory.create(
                status=settings.CONSULTANT_STATUS_CH_ACTIVE,
            )
            team = FakeTeamFactory.create(
                coach=coach,
                project=self.sprint.project_ptr,
            )
            team.add_member(
                self.super_user,
                email=faker.email(),
                name=faker.name())

        ratings = [1, 2, 4, 2]
        expected_rating = sum(ratings) / 4.0
        step = self.project.steps.all().first()

        # DO ACTION
        for index, team in enumerate(self.project.teams.all()):
            coach = team.coach
            team_step = team.steps.get(step=step)
            team_step.do_rating(
                coach.user, ratings[index], faker.text(),
            )

        # ASSERTS
        consultant = self.head_role.consultant
        interaction = Interaction.objects.filter(
            user=consultant.user,
            object_id=self.head_role.id,
            content_type=ContentType.objects.get_for_model(self.head_role)).first()
        self.assertIsNotNone(interaction)
        self.assertEqual(
            round(interaction.rating, 1),
            round(expected_rating, 1)
        )

    def test_user_rate_step_several_times(self):
        # PREPARE DATA
        ratings = [1, 2, 3]
        new_rate = [3, 4, 5]
        expected_rating = sum(new_rate) / 3.0
        step = self.project.steps.all().first()
        team_step = self.team.steps.get(step=step)

        for index, member in enumerate(self.team.team_members.all()):
            team_step.do_rating(member, ratings[index], faker.text())

        # DO ACTION
        for index, member in enumerate(self.team.team_members.all()):
            team_step.do_rating(member, new_rate[index], faker.text())

        # ASSERTS
        consultant = self.team.coach
        interaction = Interaction.objects.filter(
            user=consultant.user,
            object_id=self.coach_role.id,
            content_type=ContentType.objects.get_for_model(self.coach_role),
        ).first()
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.ratings.count(), 1)
        self.assertEqual(
            round(interaction.rating, 1),
            round(expected_rating, 1)
        )

        for index, member in enumerate(self.team.team_members.all()):
            self.assertEqual(
                team_step.get_rating_for_user(member),
                new_rate[index])

    def test_feedback_several_team_member_same_step(self):
        # PREPARE DATA
        ratings = [1, 2, 4]
        step = self.project.steps.all().first()
        team_step = self.team.steps.get(step=step)
        # DO ACTION
        for index, member in enumerate(self.team.team_members.all()):
            team_step.do_feedback(
                member, ratings[index], faker.text(),
            )

        # ASSERTS
        for index, member in enumerate(self.team.team_members.all()):
            self.assertEqual(
                team_step.get_feedback_for_user(member),
                ratings[index])
