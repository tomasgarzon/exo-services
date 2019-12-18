def when_assignment_step_post_save(sender, instance, created, *args, **kwargs):
    if created:
        project = instance.project
        for team in project.teams.filter(stream__in=instance.streams):
            instance._create_team_assignment_step(team.coach.user, team)
