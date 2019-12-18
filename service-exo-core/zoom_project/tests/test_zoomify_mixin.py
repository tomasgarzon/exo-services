from django.conf import settings
from django.test import TestCase

from exo_role.models import ExORole

from consultant.models import Consultant
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from test_utils.test_case_mixins import SuperUserTestMixin


class TestZoomify(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_zoom_settings(self):
        """
        Check that ZoomSettings for ZoomRoom and the related object settings
        are the same
        """
        sprint = FakeSprintAutomatedFactory.create()

        coaches = FakeConsultantFactory.create_batch(
            size=3, user__is_active=True,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        for coach in coaches:
            ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                consultant=coach,
                project=sprint.project_ptr,
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            )

        team = FakeTeamFactory(
            project=sprint.project_ptr,
            coach=Consultant.objects.last(),
        )

        self.assertEqual(team.settings, team.project.zoom_settings)
