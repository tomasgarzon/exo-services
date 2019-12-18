from django.conf import settings
from django.test import TestCase
from mock import patch

from exo_role.models import ExORole

from consultant.models import Consultant
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeZoomRoomTeamFactory


class TestZoomRoom(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_zoom_room_factory(self, patch):
        zoom_room = FakeZoomRoomTeamFactory()

        self.assertIsNotNone(zoom_room.meeting_id)
        self.assertIsNotNone(zoom_room.host_meeting_id)
        self.assertIsNotNone(zoom_room.content_object)
        self.assertIsNotNone(zoom_room._zoom_settings)

    def test_join_url(self):
        zoom_room = FakeZoomRoomTeamFactory()
        self.assertTrue(zoom_room.meeting_id in zoom_room.meeting_object.join_url)

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_start_url(self, patch):
        zoom_room = FakeZoomRoomTeamFactory()
        self.assertTrue(zoom_room.meeting_id in zoom_room.meeting_object.start_url)
        self.assertTrue(zoom_room.host_meeting_id in zoom_room.meeting_object.start_url)

    def test_settings_room(self):
        """
            Test settings for this ZoomRoom
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

        meeting_id = faker.word()
        team = FakeTeamFactory(
            project=sprint.project_ptr,
            coach=Consultant.objects.last(),
            zoom_id=meeting_id,
        )

        self.assertEqual(team.room.meeting_object, team)
        self.assertEqual(team.room.meeting_id, meeting_id)
        self.assertEqual(
            team.room.zoom_settings,
            team.room._zoom_settings,
        )
