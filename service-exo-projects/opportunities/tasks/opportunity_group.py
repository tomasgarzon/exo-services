from django.apps import apps
from django.conf import settings

from celery import Task

from ..opportunities_helper import (
    update_opportunity_group,
    delete_opportunity_group)
from ..helper import create_team_group


class OpportunityGroupCreateTask(Task):
    name = 'OpportunityGroupCreateTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        Team = apps.get_model('team', 'Team')
        team = Team.objects.get(id=kwargs.get('team_id'))
        create_team_group(team.project, team)


class OpportunityGroupUpdateTask(Task):
    name = 'OpportunityGroupUpdateTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return
        AdvisorRequestSettings = apps.get_model('opportunities', 'AdvisorRequestSettings')
        OpportunityTeamGroup = apps.get_model('opportunities', 'OpportunityTeamGroup')
        opportunity_group_uuid = kwargs.get('group_uuid')
        opportunity_group = OpportunityTeamGroup.objects.get(
            group_uuid=opportunity_group_uuid)
        advisor_settings = AdvisorRequestSettings.objects.get(
            id=kwargs.get('settings_id'))
        update_opportunity_group(
            advisor_settings, opportunity_group)


class OpportunityGroupDeleteTask(Task):
    name = 'OpportunityGroupDeleteTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        opportunity_group_uuid = kwargs.get('group_uuid')
        delete_opportunity_group(opportunity_group_uuid)
