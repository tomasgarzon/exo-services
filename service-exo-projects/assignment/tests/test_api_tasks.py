from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from project.tests.test_mixin import ProjectTestMixin
from project.faker_factories import FakeProjectFactory
from project.models import UserProjectRole
from team.faker_factories import FakeTeamFactory

from ..models import AssignmentTaskItem, AssignmentTaskTeam


class AssignmentTasksAPITestCase(
        UserTestMixin,
        ProjectTestMixin, APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)
        cls.team = cls.project.teams.first()
        cls.initialize(cls)

    def initialize(cls):
        cls.coach = cls.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        cls.user_coach = cls.get_user(cls)
        UserProjectRole.objects.create(
            project_role=cls.coach,
            user=cls.user_coach,
            teams=cls.project.teams.all())
        cls.user_participant = UserProjectRole.objects.create_participant(
            project=cls.project,
            teams=cls.project.teams.all(),
            name=faker.name(),
            email=faker.email()).user
        cls.other_user_participant = UserProjectRole.objects.create_participant(
            project=cls.project,
            name=faker.name(),
            teams=cls.project.teams.all(),
            email=faker.email()).user
        cls.project._active_roles(cls.super_user)

    def get_task_item_and_detail_route_url(self, done=True):
        task_item = AssignmentTaskItem.objects.first()
        assignment_step = task_item.assignment_task.block.assignments_step.all().first()
        kwargs = {
            'project_pk': assignment_step.step.project.pk,
            'team_pk': self.team.pk,
            'pk': assignment_step.step.pk
        }
        if done:
            url = reverse('api-view:project-step-tasks-done', kwargs=kwargs)
        else:
            url = reverse('api-view:project-step-tasks-undone', kwargs=kwargs)
        return task_item, url

    def add_user_to_team(self):
        team = FakeTeamFactory.create(
            project=self.project,
            created_by=self.project.created_by,
            stream=self.project.streams.first())
        user_role = UserProjectRole.objects.create_participant(
            project=self.project,
            teams=[team],
            name=faker.name(),
            email=faker.email())
        user_role.activate(self.project.created_by)
        user_coach = self.get_user()
        UserProjectRole.objects.create(
            project_role=self.coach,
            user=user_coach,
            teams=[team])
        return user_role.user, team, user_coach

    def test_assignment_step_task_done(self):
        # PREPARE DATA
        team_member = self.user_participant
        task_item, url = self.get_task_item_and_detail_route_url(done=True)
        data = {'pk_list': [task_item.pk]}
        new_user, new_team, new_team_coach = self.add_user_to_team()
        inputs = (
            (self.super_user, True),
            (self.user_coach, True),
            (team_member, True),
            (new_user, False),
            (new_team_coach, False),
        )

        # DO ACTION
        for user_do_action, allowed_do_action in inputs:
            self.setup_credentials(user_do_action)
            response = self.client.post(url, data=data, format='json')

            # ASSERTS
            if allowed_do_action:
                self.assertTrue(status.is_success(response.status_code))
                self.assertEqual(
                    response.json()[0].get('status'),
                    settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)
                self.assertEqual(AssignmentTaskTeam.objects.get(
                    assignment_step_team__team=self.team,
                    assignment_task_item=AssignmentTaskItem.objects.first()).status,
                    settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)
            else:
                self.assertTrue(status.is_client_error(response.status_code))

    def test_assignment_step_mark_task_undone(self):
        # PREPARE DATA
        team_member = self.user_participant
        task_item, url = self.get_task_item_and_detail_route_url(done=False)
        data = {'pk_list': [task_item.pk]}
        new_user, new_team, new_team_coach = self.add_user_to_team()
        inputs = (
            (self.super_user, True),
            (self.user_coach, True),
            (team_member, True),
            (new_user, False),
            (new_team_coach, False),
        )

        # DO ACTION
        for user_do_action, allowed_do_action in inputs:
            self.setup_credentials(user_do_action)
            response = self.client.post(url, data=data, format='json')

            # ASSERTS
            if allowed_do_action:
                self.assertTrue(status.is_success(response.status_code))
                self.assertEqual(response.json()[0].get('status'), settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO)
                self.assertEqual(AssignmentTaskTeam.objects.get(
                    assignment_step_team__team=self.team,
                    assignment_task_item=AssignmentTaskItem.objects.first()).status,
                    settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO)
            else:
                self.assertTrue(status.is_client_error(response.status_code))
