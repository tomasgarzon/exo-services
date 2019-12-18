from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from guardian.shortcuts import assign_perm

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from team.faker_factories import FakeTeamFactory
from project.faker_factories import FakeStepFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..models import AssignmentTaskItem, AssignmentTaskTeam
from ..conf import settings
from .assignments_mixin import AssignmentsMixin


class AssignmentStepAPITasksTestCase(SuperUserTestMixin, AssignmentsMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.prepare_data()
        self.populate_assignments_version_2(
            self.sprint_automated,
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)

    def prepare_data(self):
        self.sprint_automated = FakeSprintAutomatedFactory.create()
        self.team = FakeTeamFactory.create(project=self.sprint_automated.project_ptr)
        self.step = FakeStepFactory.create(project=self.team.project)
        user = FakeUserFactory.create(is_active=True)
        self.add_user_to_team(user, self.team)

    def add_user_to_team(self, user, team):
        team.add_member(
            user_from=self.super_user,
            email=user.email,
            name=user.short_name,
        )
        assign_perm(settings.PROJECT_PERMS_VIEW_PROJECT, user, team.project)
        self.team.activate(user=user)

    def get_task_item_and_detail_route_url(self, done=True):
        task_item = AssignmentTaskItem.objects.first()
        assignment_step = task_item.assignment_task.block.assignments_step.all().first()
        kwargs = {
            'project_id': assignment_step.step.project.pk,
            'team_id': self.team.pk,
            'pk': assignment_step.step.pk
        }

        if done:
            url = reverse('api:project:step:step-tasks-done', kwargs=kwargs)
        else:
            url = reverse('api:project:step:step-tasks-undone', kwargs=kwargs)

        return task_item, url

    def test_assignment_step_task_done(self):
        # PREPARE DATA
        new_user = FakeUserFactory.create(is_active=True)
        team_member = self.team.team_members.first()
        task_item, url = self.get_task_item_and_detail_route_url(done=True)
        data = {'pk_list': [task_item.pk]}
        new_team = FakeTeamFactory.create()
        self.add_user_to_team(new_user, new_team)
        inputs = (
            (self.super_user, True, '123456'),
            (self.team.coach.user, True, '123456'),
            (team_member, True, team_member.short_name),
            (new_user, False, new_user.short_name),
            (new_team.coach.user, False, '123456'),
        )

        # DO ACTION
        for user_do_action, allowed_do_action, password_login in inputs:
            self.client.login(username=user_do_action.username, password=password_login)
            response = self.client.post(url, data=data, format='json')

            # ASSERTS
            if allowed_do_action:
                self.assertTrue(status.is_success(response.status_code))
                self.assertEqual(response.json()[0].get('status'), settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)
                self.assertEqual(AssignmentTaskTeam.objects.get(
                    assignment_step_team__team=self.team,
                    assignment_task_item=AssignmentTaskItem.objects.first()).status,
                    settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)
            else:
                self.assertTrue(status.is_client_error(response.status_code))

    def test_assignment_step_mark_task_undone(self):
        # PREPARE DATA
        new_user = FakeUserFactory.create(is_active=True)
        team_member = self.team.team_members.first()
        task_item, url = self.get_task_item_and_detail_route_url(done=False)
        data = {'pk_list': [task_item.pk]}
        new_team = FakeTeamFactory.create()
        self.add_user_to_team(new_user, new_team)
        inputs = (
            (self.super_user, True, '123456'),
            (self.team.coach.user, True, '123456'),
            (team_member, True, team_member.short_name),
            (new_user, False, new_user.short_name),
            (new_team.coach.user, False, '123456'),
        )

        # DO ACTION
        for user_do_action, allowed_do_action, password_login in inputs:
            self.client.login(username=user_do_action.username, password=password_login)
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
