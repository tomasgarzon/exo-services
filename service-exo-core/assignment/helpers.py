from project.models import Project
from team.models import Team

from .models import Assignment


def get_assignment_team(tags):
    projects = Project.objects.filter(
        slug__in=tags,
    )
    if not projects:
        return
    project = projects.first()
    assignments = Assignment.objects.filter(
        slug__in=tags,
        project=project,
    )
    if not assignments:
        return
    assignment = assignments.first()
    teams = Team.objects.filter(
        slug__in=tags,
        project=project,
    )
    if not teams:
        return
    team = teams.first()
    assignment_team = assignment.teams.filter(team=team).first()
    return assignment_team
