from django.urls import reverse
from django.test import tag
from django import test
from django.conf import settings
from django.test import Client

from rest_framework import status
from exo_role.models import ExORole

from utils.faker_factory import faker
from utils.dates import decrease_date
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from relation.models import ConsultantProjectRole
from project.faker_factories import FakeProjectFactory
from consultant.faker_factories import FakeConsultantFactory
from team.faker_factories import FakeTeamFactory
from agreement.faker_factories import FakeAgreementFactory
from agreement.models import UserAgreement
from invitation.models import Invitation
from consultant.models import Consultant

from ..helpers import UserRedirectController


class TestUserRedirectController(
        UserTestMixin,
        SuperUserTestMixin,
        test.TestCase
):

    def setUp(self):
        self.create_user()
        self.create_superuser()

    def test_redirect_no_projects_simple(self):
        # DO ACTION
        url, zone = UserRedirectController.redirect_url(self.user)

        # ASSERTS
        self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
        self.assertFalse(zone)

    def test_redirect_no_projects_superuser(self):
        # DO ACTION
        url, zone = UserRedirectController.redirect_url(self.super_user)

        # ASSERTS
        self.assertEqual(url, reverse('dashboard:home'))
        self.assertTrue(zone)

    def test_redirect_projects_superuser(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        team = FakeTeamFactory.create(
            project=project,
        )

        # DO ACTION
        team.add_member(
            user_from=self.super_user,
            email=self.super_user.email,
            name=self.super_user.short_name,
        )

        # ASSERTS
        url, zone = UserRedirectController.redirect_url(self.super_user)
        self.assertTrue(zone)
        self.assertEqual(url, reverse('dashboard:home'))

    def test_one_project_roles(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        inputs = [
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_REPORTER),
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_ALIGN_TRAINER),
        ]

        for exo_role in inputs:
            # DO ACTION
            relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                project=project,
                consultant=FakeConsultantFactory.create(user__is_active=True),
                exo_role=exo_role,
            )

            # ASSERTS
            url, zone = UserRedirectController.redirect_url(relation.consultant.user)
            self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
            self.assertFalse(zone)

    def test_several_projects_not_started(self):
        # PREPARE DATA
        projects = FakeProjectFactory.create_batch(
            size=2, end=None,
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED,
        )
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[0],
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[1],
            consultant=relation.consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        # DO ACTION
        url, zone = UserRedirectController.redirect_url(relation.consultant.user)

        # ASSERTS
        self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
        self.assertFalse(zone)

    def test_several_projects_several_statuses(self):
        # PREPARE DATA
        projects = FakeProjectFactory.create_batch(
            size=2, end=None,
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED,
        )
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[0],
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[1],
            consultant=relation.consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        project = projects[0]
        project.end = decrease_date(days=5)
        project.save()
        FakeTeamFactory.create(
            coach=relation.consultant,
            project=projects[1],
        )

        # DO ACTION
        url, zone = UserRedirectController.redirect_url(relation.consultant.user)

        # ASSERTS
        self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
        self.assertFalse(zone)

    def test_several_projects_finished(self):
        # PREPARE DATA
        projects = FakeProjectFactory.create_batch(
            size=2, end=decrease_date(days=5),
            status=settings.PROJECT_CH_PROJECT_STATUS_FINISHED,
        )
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[0],
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=projects[1],
            consultant=relation.consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        # DO ACTION
        url, zone = UserRedirectController.redirect_url(relation.consultant.user)

        # ASSERTS
        self.assertEqual(url, settings.FRONTEND_CIRCLES_PAGE)
        self.assertFalse(zone)

    def test_participant_project_version_2(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        team = FakeTeamFactory.create(
            project=project,
            user_from=self.super_user,
        )
        user = team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )

        # DO ACTION
        url, zone = UserRedirectController.redirect_url(user)

        # ASSERTS
        url_redirect = settings.FRONTEND_PROJECT_STEP_PAGE.format(
            **{
                'project_id': project.id,
                'team_id': project.teams.first().pk,
                'step_id': project.current_step().pk,
                'section': 'learn'})
        self.assertEqual(url, url_redirect)
        self.assertFalse(zone)

    def test_consultant_tos_pending(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        previous_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )

        # ACTION
        user_agreement = UserAgreement.objects.create(
            agreement=previous_agreement,
            user=consultant.user,
        )
        Invitation.objects.create_user_agreement(
            self.super_user,
            consultant.user,
            user_agreement,
        )

        # ASSERTS
        self.assertTrue(consultant.has_tos_invitations_pending)
        self.assertFalse(consultant.can_access_to_dashboard)
        url, zone = UserRedirectController.redirect_url(consultant.user)
        url_expected = settings.FRONTEND_INVITATION_PAGE.format(
            **{'hash': consultant.get_tos_invitation_pending().hash})
        self.assertEqual(
            url,
            url_expected,
        )
        self.assertFalse(zone)

    @tag('sequencial')
    def test_consultant_pending_to_ecosystem(self):
        # PREPARE DATA
        consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        user = consultant.user
        user.set_password('123456')
        user.save()

        client = Client()

        # DO ACTION
        response_login = client.login(username=consultant.user.email, password='123456')
        response = client.get(
            settings.FRONTEND_CIRCLES_PAGE)

        # ASSERTS
        self.assertTrue(response_login)
        self.assertTrue(status.is_redirect(response.status_code))
