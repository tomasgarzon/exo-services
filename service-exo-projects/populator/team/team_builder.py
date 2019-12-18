from django.contrib.auth import get_user_model

from populate.populator.builder import Builder

from learning.models import UserMicroLearning
from team.models import Team, UserTeamRole
from opportunities.models import OpportunityTeamGroup


class TeamBuilder(Builder):

    def create_microlearnings(self, member, team):
        microlearnings = member.get('microlearnings', [])
        for microlearning_data in microlearnings:
            step = team.project.steps.all()[microlearning_data.get('step') - 1]
            step_stream = step.streams.get(stream=team.stream)
            microlearning = step_stream.microlearning

            user_micro_learning = UserMicroLearning.objects.create(
                microlearning=microlearning,
                user=member.get('user'),
                team=team
            )

            # Simulate Typeform webhook
            user_micro_learning.add_typeform_response(
                score=microlearning_data.get('score'),
                response=''
            )

    def create_team_members(self, team):
        members = self.data.get('members', [])
        for member in members:
            project_role = team.project.team_roles.get(
                role=member.get('role'))
            if member.get('user'):
                user = member.get('user')
            else:
                user = get_user_model().objects.get(participant__email=member.get('email'))
            UserTeamRole.objects.get_or_create(
                created_by=team.created_by,
                user=user,
                team=team,
                team_role=project_role,
                active=member.get('active', True))

            self.create_microlearnings(member, team)

    def update_roles(self, team):
        if not team.project.is_draft:
            for user_role in team.user_team_roles.all():
                user_role.activate(team.project.created_by)

    def create_opportunity_group(self, team):
        if self.data.get('group_uuid'):
            OpportunityTeamGroup.objects.update_or_create(
                team=team,
                defaults={
                    'group_uuid': self.data.get('group_uuid')})

    def create_object(self):
        project = self.data.get('project')
        stream = project.streams.get(name=self.data.get('stream'))
        team, _ = Team.objects.get_or_create(
            uuid=self.data.get('uuid'),
            name=self.data.get('name'),
            project=project,
            stream=stream,
            image=self.data.get('image'),
            created_by=self.data.get('created_by'),
        )

        self.create_team_members(team)
        self.update_roles(team)
        self.create_opportunity_group(team)
        return team
