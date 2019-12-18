from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from rest_framework import status

from exo_role.models import ExORole

from files.faker_factories import FakeUploadedFileFactory
from team.faker_factories import FakeTeamFactory
from project.faker_factories import FakeStepFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import FakeAssignmentStepFactory
from ..models import AssignmentStepTeam, AssignmentStep
from ..conf import settings
from .assignments_mixin import AssignmentsMixin


class AssignmentStepAPITestCase(SuperUserTestMixin, UserTestMixin, AssignmentsMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.prepare_data()

    def prepare_data(self):
        self.sprint_automated = FakeSprintAutomatedFactory.create()
        self.team = FakeTeamFactory.create(project=self.sprint_automated.project_ptr)
        self.step = FakeStepFactory.create(project=self.team.project)
        self.populate_assignments_version_2(
            self.sprint_automated,
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)
        consultant_manager_user = FakeUserFactory.create()
        consultant_for_manager_role = FakeConsultantFactory.create(
            user=consultant_manager_user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        team_member = FakeUserFactory.create()
        self.team.team_members.add(self.user)
        self.team.team_members.add(team_member)

        self.manager_role, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.sprint_automated.project_ptr,
            consultant=consultant_for_manager_role,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )

        self.sprint_automated.launch(self.super_user)

    def test_assignment_step_teams_creation(self):
        # DO ACTION
        FakeAssignmentStepFactory.create(step=self.step, streams=self.team.stream)

        # ASSERTS
        self.assertTrue(AssignmentStepTeam.objects.filter(
            assignment_step__streams=self.team.stream,
            team=self.team).exists())

    def test_assignment_step_assignments_creation(self):
        # PREPARE DATA
        assignment_step = AssignmentStep.objects.filter_by_project(self.sprint_automated.project_ptr).first()
        kwargs = {
            'project_id': assignment_step.step.project.pk,
            'team_id': self.team.pk,
            'pk': assignment_step.step.pk
        }
        url = reverse('api:project:step:step-detail', kwargs=kwargs)
        self.client.login(username=self.super_user.username, password='123456')

        # DO ACTION
        response = self.client.get(url, format='json')

        # ASSERTS
        assignment = response.data.get('assignments')[0]
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('name'), assignment_step.step.name)
        self.assertTrue(len(response.data.get('assignments')))
        self.assertEqual(assignment.get('name'), assignment_step.name)
        self.assertTrue(len(assignment.get('blocks')))

    def test_assignment_step_deliverables_files(self):
        # PREPARE DATA
        assignment_step_team = self.team.assignment_step_teams.all().first()
        user_coach = self.team.coach.user
        step_team_content_type = ContentType.objects.get_for_model(assignment_step_team)

        FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk,
            visibility=settings.FILES_VISIBILITY_GROUP)
        FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk,
            visibility=settings.FILES_VISIBILITY_PRIVATE)
        FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk,
            visibility=settings.FILES_VISIBILITY_PRIVATE,
            created_by=self.team.team_members.last())

        file_without_visibility_relation = FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk)
        file_without_visibility_relation.visibility.all().delete()

        # DO ACTION
        files_response_for_superuser = assignment_step_team.uploaded_files_with_visibility(self.super_user)
        files_response_for_user_head_coach = assignment_step_team.uploaded_files_with_visibility(user_coach)
        files_response_for_team_member = assignment_step_team.uploaded_files_with_visibility(
            self.team.team_members.first())
        files_response_for_team_member_other = assignment_step_team.uploaded_files_with_visibility(
            self.team.team_members.last())

        # ASSERTS
        self.assertEqual(len(files_response_for_superuser), 4)
        self.assertEqual(len(files_response_for_user_head_coach), 4)
        self.assertEqual(len(files_response_for_team_member), 2)
        self.assertEqual(len(files_response_for_team_member_other), 3)

    def test_uploaded_file_visibility_toggle_api(self):
        # PREPARE DATA
        self.client.login(username=self.super_user.username, password='123456')

        assignment_step_team = self.team.assignment_step_teams.all().first()
        step_team_content_type = ContentType.objects.get_for_model(assignment_step_team)

        file = FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk,
            created_by=self.super_user,
        )
        url = reverse('api:file-versioned:visibility-toggle', kwargs={'pk': file.pk})
        old_visibility = file.get_visibility_code()

        # PRE ASSERTS
        self.assertIsNotNone(old_visibility)

        # DO ACTION
        response = self.client.put(url)

        # ASSERTS
        self.assertIsNotNone(response.json().get('visibility'))
        self.assertNotEqual(response.json().get('visibility'), old_visibility)
