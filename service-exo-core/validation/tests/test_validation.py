from django import test

from team.faker_factories import FakeTeamFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..validators import (
    TeamValidator, TeamZoomValidator,
    ParticipantPasswordValidator
)
from ..conf import settings


class ProjectTeamValidatorTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        self.create_superuser()

    def test_validation_no_teams(self):
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
        )
        validator = TeamValidator(sprint.project_ptr)
        validator.validate()
        self.assertEqual(sprint.project_ptr.validations.count(), 1)
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 1,
        )

    def test_validation_teams(self):
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
        )
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
        )
        validator = TeamValidator(sprint.project_ptr)
        validator.validate()
        self.assertEqual(sprint.project_ptr.validations.count(), 1)
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 0,
        )
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_fixed().count(), 1,
        )

        team.delete()
        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 1,
        )
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_fixed().count(), 0,
        )

    def test_validation_zoom_team(self):
        """
            Validation related to Zoom configuration for Teams
        """
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
        )
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
        )

        validator = TeamZoomValidator(sprint.project_ptr)
        validator.validate()
        self.assertEqual(sprint.project_ptr.validations.count(), 0)

        team.zoom_id = faker.word()
        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 1,
        )

        # ##
        # One team with his own host_meeting_id
        # ##
        room = team.room
        room.host_meeting_id = faker.word()
        room.save()

        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 0,
        )

        # ##
        # Almost 1 team has no host_meeting_id
        # ##
        team2 = FakeTeamFactory.create(
            project=sprint.project_ptr,
        )

        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 1,
        )

        team2.zoom_id = faker.word()
        room2 = team2.room
        room2.host_meeting_id = faker.word()
        room2.save()

        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 0,
        )

        # ##
        # No Team for this Project has a zoom_id, neither a host_meeting_id
        # ##
        team.zoom_id = None
        team2.zoom_id = None

        validator.validate()
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 0,
        )

    def test_validation_default_password(self):
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
        )
        validator = ParticipantPasswordValidator(sprint.project_ptr)
        validator.validate()
        self.assertEqual(sprint.project_ptr.validations.count(), 1)
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 1,
        )
        project_settings = sprint.project_ptr.settings
        project_settings.launch['fix_password'] = faker.word()
        project_settings.save()
        validator.validate()
        self.assertEqual(sprint.project_ptr.validations.count(), 1)
        self.assertEqual(
            sprint.project_ptr.validations
            .filter_by_status_pending().count(), 0,
        )
