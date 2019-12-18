from ..models import AssignmentStep


def post_save_team(sender, instance, created, *args, **kwargs):
    if created:
        assignments = AssignmentStep.objects.filter_by_project(
            instance.project).filter_by_stream(instance.stream)

        for assignment_step in assignments:
            assignment_step._create_team_assignment_step(instance.created_by, instance)


def post_stream_changed(sender, team, *args, **kwargs):
    team.assignment_step_teams.all().delete()
    post_save_team(sender, team, True)
