import random

from django.conf import settings
from django.test import TestCase
from django.test import tag

from exo_role.models import ExORole

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from test_utils.redis_test_case_mixin import RedisTestCaseMixin
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from utils.faker_factory import faker
from utils.dates import string_to_datetime
from forum.models import Post

from ..models import QASession


class QASessionTest(
        UserTestMixin,
        SuperUserTestMixin,
        RedisTestCaseMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.initialize()

    def initialize(self):
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_team = FakeTeamFactory.create(project=sprint.project_ptr)
        new_team.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name,
        )
        consultants = [
            FakeConsultantProjectRoleFactory.create(
                project=sprint.project_ptr,
                consultant=FakeConsultantFactory(user__is_active=True),
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
                exo_role_other_name='Swarm',
                status=settings.RELATION_ROLE_CH_ACTIVE,
            ) for i in range(5)
        ]
        self.team = new_team
        self.sprint = sprint
        self.advisors = consultants

    def test_filter_qa_session(self):
        # PREPARE DATA
        # Session1: 10-10-2018 10:00 to 10-10-2018 14:00
        # Session 2: 10-11-2018 10:00 to 10-11-2018 14:00
        qa_session1 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 10, 10:00'),
            end_at=string_to_datetime('2018, 10, 10, 14:00'),
        )
        qa_session2 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 11, 10:00'),
            end_at=string_to_datetime('2018, 10, 11, 14:00'),
        )
        for c_project_role in self.advisors:
            qa_session1.qa_session_advisors.create(consultant_project_role=c_project_role)
            qa_session2.qa_session_advisors.create(consultant_project_role=c_project_role)

        # ASSERTS
        inputs = [
            string_to_datetime('2018, 10, 10, 1:00'),
            string_to_datetime('2018, 10, 10, 18:00'),
            string_to_datetime('2018, 10, 9, 10:00'),
            string_to_datetime('2018, 10, 11, 10:10'),
            string_to_datetime('2018, 10, 12, 10:00'),
        ]

        outputs = [
            qa_session1, qa_session2, qa_session1, qa_session2, qa_session2
        ]

        for index, when in enumerate(inputs):
            qa_session = self.team.qa_sessions.select_session_by_datetime(when)
            self.assertEqual(qa_session.session, outputs[index])

    def test_total_answers_by_participant(self):
        # PREPARE DATA
        qa_session1 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 10, 10:00'),
            end_at=string_to_datetime('2018, 10, 10, 14:00'),
        )
        qa_session_team_1 = qa_session1.teams.get(team=self.team)

        for c_project_role in self.advisors:
            qa_session1.qa_session_advisors.create(consultant_project_role=c_project_role)

        qa_session2 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 11, 10:00'),
            end_at=string_to_datetime('2018, 10, 11, 14:00'),
        )
        qa_session_team_2 = qa_session2.teams.get(team=self.team)

        for c_project_role in self.advisors:
            qa_session2.qa_session_advisors.create(consultant_project_role=c_project_role)

        new_user = self.team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )

        # DO ACTIONS
        post = Post.objects.create_project_qa_session_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
            qa_session_team=qa_session_team_1,
        )
        post2 = Post.objects.create_project_qa_session_post(
            user_from=self.user,
            title=' '.join(faker.words()),
            description=faker.text(),
            qa_session_team=qa_session_team_2,
        )
        post3 = Post.objects.create_project_qa_session_post(
            user_from=new_user,
            title=' '.join(faker.words()),
            description=faker.text(),
            qa_session_team=qa_session_team_2,
        )

        post.reply(self.advisors[0].consultant.user, faker.text())
        post.reply(self.advisors[2].consultant.user, faker.text())
        post2.reply(self.advisors[0].consultant.user, faker.text())
        post2.reply(self.advisors[1].consultant.user, faker.text())
        post3.reply(self.advisors[2].consultant.user, faker.text())
        post3.reply(self.advisors[3].consultant.user, faker.text())
        post3.reply(self.advisors[0].consultant.user, faker.text())

        # ASSERTS
        self.assertEqual(qa_session_team_1.questions.count(), 1)
        self.assertEqual(
            qa_session_team_1.total_answers_by_participant(self.user), 2)
        self.assertEqual(
            qa_session_team_1.total_answers_by_participant(new_user), 0)
        self.assertEqual(
            qa_session_team_2.questions.count(), 2)
        self.assertEqual(
            qa_session_team_2.total_answers_by_participant(self.user), 2)
        self.assertEqual(
            qa_session_team_2.total_answers_by_participant(new_user), 3)

    @tag('sequencial')
    def test_total_rating(self):
        # PREPARE DATA
        qa_session1 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 10, 10:00'),
            end_at=string_to_datetime('2018, 10, 10, 14:00'),
        )

        for c_project_role in self.advisors:
            qa_session1.qa_session_advisors.create(consultant_project_role=c_project_role)

        team_qa_session_1 = qa_session1.teams.get(team=self.team)

        new_user = self.team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )
        users = [self.user, new_user]
        inputs = [
            [1, 4, 3],
            [2, (4, 5), 2],
            [(1, 4), 2, (1, 1)],
            [4, (2, 3), 3],
            [1, 5, (5, 5)],
        ]

        # DO ACTIONS
        for k in range(len(inputs)):
            post = Post.objects.create_project_qa_session_post(
                user_from=random.choice(users),
                title=' '.join(faker.words()),
                description=faker.text(),
                qa_session_team=team_qa_session_1,
            )
            for j in range(3):
                user = random.choice(self.advisors).consultant.user
                answer = post.reply(user, faker.text())
                rating = inputs[k][j]
                if isinstance(rating, tuple):
                    for index, user in enumerate(users):
                        answer.do_rating(
                            user,
                            rating[index])

                else:
                    answer.do_rating(
                        random.choice(users),
                        rating)

        #  ASSERTS
        self.assertEqual(round(team_qa_session_1.rating_average, 1), 2.7)

    def test_total_rating_avg_method_with_differents_users(self):
        # PREPARE DATA
        qa_session1 = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2018, 10, 10, 10:00'),
            end_at=string_to_datetime('2018, 10, 10, 14:00'),
        )

        for c_project_role in self.advisors:
            qa_session1.qa_session_advisors.create(consultant_project_role=c_project_role)

        team_qa_session_1 = qa_session1.teams.get(team=self.team)

        new_user = self.team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )

        users = [self.user, new_user]
        inputs = [
            [4, 4, 4],
            [4, (4, 4), 4],
            [(4, 4), 4, (4, 4)],
            [4, (4, 4), 4],
            [4, 4, (4, 4)],
        ]

        # DO ACTIONS
        for k in range(len(inputs)):
            post = Post.objects.create_project_qa_session_post(
                user_from=random.choice(users),
                title=' '.join(faker.words()),
                description=faker.text(),
                qa_session_team=team_qa_session_1,
            )
            for j in range(3):
                user = random.choice(self.advisors).consultant.user
                answer = post.reply(user, faker.text())
                rating = inputs[k][j]
                if isinstance(rating, tuple):
                    for index, user in enumerate(users):
                        answer.do_rating(
                            user,
                            rating[index])

                else:
                    answer.do_rating(
                        random.choice(users),
                        rating)

        #  ASSERTS
        self.assertEqual(round(team_qa_session_1.rating_average, 1), 4)
