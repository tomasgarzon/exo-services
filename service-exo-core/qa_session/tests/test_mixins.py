from django.conf import settings

from exo_role.models import ExORole

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from forum.models import Post
from qa_session.models import QASession
from relation.faker_factories import FakeConsultantProjectRoleFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from utils.dates import string_to_datetime

from utils.faker_factory import faker


class QASessionTestMixin:

    def get_files_example(self, num=1):
        files = []
        for i in range(num):
            file = {
                'filestack_status': 'Stored',
                'filename': '{}.png'.format(faker.word()),
                'mimetype': 'image/png',
                'url': 'https://cdn.filestackcontent.com/{}'.format(faker.numerify()),
            }
            files.append(file)

        return files

    def initialize_swarms(self, superuser, user):
        self.secondary_user = FakeUserFactory.create()
        self.sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        self.team_A = FakeTeamFactory.create(
            project=self.sprint.project_ptr)
        self.team_B = FakeTeamFactory.create(
            project=self.sprint.project_ptr)

        self.team_A.add_member(
            user_from=superuser,
            email=user.email,
            name=user.short_name)

        self.team_B.add_member(
            user_from=superuser,
            email=self.secondary_user.email,
            name=self.secondary_user.short_name)

        self.advisors_first = [
            FakeConsultantProjectRoleFactory.create(
                project=self.sprint.project_ptr,
                consultant=FakeConsultantFactory(user__is_active=True),
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
                exo_role_other_name='Swarm',
                status=settings.RELATION_ROLE_CH_ACTIVE,
            ) for i in range(4)
        ]
        self.advisors_second = [
            FakeConsultantProjectRoleFactory.create(
                project=self.sprint.project_ptr,
                consultant=FakeConsultantFactory(user__is_active=True),
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
                exo_role_other_name='Swarm',
                status=settings.RELATION_ROLE_CH_ACTIVE,
            ) for i in range(3)
        ]

        self.qa_session_first = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2019, 04, 20, 11:00'),
            end_at=string_to_datetime('2019, 04, 20, 12:00'),
        )

        self.qa_session_second = QASession.objects.create(
            project=self.sprint.project_ptr,
            start_at=string_to_datetime('2019, 04, 26, 13:00'),
            end_at=string_to_datetime('2019, 04, 26, 14:00'),
        )

        for c_project_role in self.advisors_first:
            self.qa_session_first.qa_session_advisors.create(consultant_project_role=c_project_role)
            self.qa_session_second.qa_session_advisors.create(consultant_project_role=c_project_role)

        self.posts_first_A = [
            Post.objects.create_project_qa_session_post(
                user_from=user,
                title=' '.join(faker.words()),
                description=faker.text(),
                qa_session_team=self.qa_session_first.teams.get(
                    team=self.team_A)
            ) for i in range(6)
        ]

        post = self.posts_first_A[0]
        post.reply(self.advisors_first[0].consultant.user, faker.text())
        post.reply(self.advisors_first[1].consultant.user, faker.text())
        post.reply(self.advisors_first[2].consultant.user, faker.text())

        self.post_first_B = [
            Post.objects.create_project_qa_session_post(
                user_from=self.secondary_user,
                title=' '.join(faker.words()),
                description=faker.text(),
                qa_session_team=self.qa_session_first.teams.get(
                    team=self.team_B)
            ) for i in range(4)
        ]

        post = self.post_first_B[0]
        post.reply(self.advisors_first[0].consultant.user, faker.text())
        post.reply(self.advisors_first[1].consultant.user, faker.text())
        post.reply(self.advisors_first[0].consultant.user, faker.text())
