from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from files.faker_factories import FakeUploadedFileFactory
from files.models import UploadedFile
from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from project.tests.test_mixin import ProjectTestMixin, request_mock_account
from project.faker_factories import FakeProjectFactory
from project.models import UserProjectRole


class AssignmentDeliverablesAPITestCase(
        UserTestMixin,
        ProjectTestMixin, APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        request_mock_account.reset()
        request_mock_account.add_mock(
            cls.super_user, is_consultant=False, is_superuser=True)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)
        cls.team = cls.project.teams.first()

    def test_assignment_step_teams_creation(self):
        # ASSERTS
        for team in self.project.teams.all():
            self.assertTrue(team.assignment_step_teams.exists())

    @requests_mock.Mocker()
    def test_create_deliverable(self, mock_request):
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        assignment_step_team = self.team.assignment_step_teams.all().first()
        url = reverse('api-view:files:add', kwargs={
            'class_name': 'assignmentstepteam',
            'object_id': assignment_step_team.pk})
        data = {
            'filestack_status': 'Stored',
            'url': 'https://cdn.filestackcontent.com/Lr59QG8oQRWliC6x70cx',
            'filename': 'gato.jpg',
            'mimetype': 'image/jpeg'}

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_delete_deliverable(self, mock_request):
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        assignment_step_team = self.team.assignment_step_teams.all().first()
        url = reverse('api-view:files:add', kwargs={
            'class_name': 'assignmentstepteam',
            'object_id': assignment_step_team.pk})
        data = {
            'filestack_status': 'Stored',
            'url': 'https://cdn.filestackcontent.com/Lr59QG8oQRWliC6x70cx',
            'filename': 'gato.jpg',
            'mimetype': 'image/jpeg'}
        response = self.client.post(url, data=data)
        pk = response.json().get('pk')

        # DO ACTION
        url = reverse('api-view:files:update-delete', kwargs={
            'class_name': 'assignmentstepteam',
            'object_id': assignment_step_team.pk,
            'pk': pk})
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(UploadedFile.objects.filter(pk=pk).exists())

    def test_assignment_step_deliverables_files(self):
        # PREPARE DATA
        assignment_step_team = self.team.assignment_step_teams.all().first()
        coach = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        user_coach = self.get_user()
        UserProjectRole.objects.create(
            project_role=coach,
            user=user_coach,
            teams=self.project.teams.all())
        user_participant = UserProjectRole.objects.create_participant(
            project=self.project,
            teams=self.project.teams.all(),
            name=faker.name(),
            email=faker.email()).user
        other_user_participant = UserProjectRole.objects.create_participant(
            project=self.project,
            name=faker.name(),
            teams=self.project.teams.all(),
            email=faker.email()).user
        step_team_content_type = ContentType.objects.get_for_model(assignment_step_team)
        self.project._active_roles(self.super_user)

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
            created_by=user_participant)

        file_without_visibility_relation = FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk)
        file_without_visibility_relation.visibility.all().delete()

        # DO ACTION
        files_response_for_superuser = assignment_step_team.uploaded_files_with_visibility(self.super_user)
        files_response_for_user_coach = assignment_step_team.uploaded_files_with_visibility(user_coach)
        files_response_for_team_member = assignment_step_team.uploaded_files_with_visibility(
            other_user_participant)
        files_response_for_team_member_other = assignment_step_team.uploaded_files_with_visibility(
            user_participant)

        # ASSERTS
        self.assertEqual(len(files_response_for_superuser), 4)
        self.assertEqual(len(files_response_for_user_coach), 4)
        self.assertEqual(len(files_response_for_team_member), 2)
        self.assertEqual(len(files_response_for_team_member_other), 3)

    @requests_mock.Mocker()
    def test_uploaded_file_visibility_toggle_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        assignment_step_team = self.team.assignment_step_teams.all().first()
        step_team_content_type = ContentType.objects.get_for_model(assignment_step_team)

        file = FakeUploadedFileFactory(
            content_type=step_team_content_type,
            object_id=assignment_step_team.pk,
            created_by=self.super_user,
        )
        url = reverse('api-view:files:visibility-toggle', kwargs={'pk': file.pk})
        old_visibility = file.get_visibility_code()

        # PRE ASSERTS
        self.assertIsNotNone(old_visibility)

        # DO ACTION
        response = self.client.put(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(response.json().get('visibility'))
        self.assertNotEqual(response.json().get('visibility'), old_visibility)
