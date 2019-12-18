def post_save_assignment(sender, instance, action, pk_set, *args, **kwargs):
    if action == 'post_add':
        project = instance.project
        streams = instance.project.streams.filter(id__in=pk_set)
        for team in project.teams.filter(stream__in=streams):
            instance._create_team_assignment_step(team.created_by, team)
