from django.core.management import call_command

from assignment.models import AssignmentStep


class AssignmentProjectMixin:

    def get_assignments_template(self):
        return self.settings.template_assignments

    def create_team_assignments(self, team):
        assignments = AssignmentStep.objects.filter_by_project(self).filter_by_stream(team.stream)

        for assignment_step in assignments:
            assignment_step._create_team_assignment_step(team.coach.user, team)

    def delete_team_assignments_when_team_modified(self, team):
        pass

    def delete_team_assignments(self, team):
        team.assignment_step_teams.all().delete()

    def update_assignments_template(self, template=None):
        AssignmentStep.objects.filter_by_project(self).delete()

        if template:
            call_command(
                'populate_assignments',
                project=[self.pk],
                template_assignments=[template],
                delete=[1],
            )
