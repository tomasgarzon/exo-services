def post_save_team_handler(sender, instance, created, *args, **kwargs):
    if created:
        for step in instance.project.steps.all():
            step.teams.get_or_create(team=instance)


def post_save_step_handler(sender, instance, created, *args, **kwargs):
    if created:
        for team in instance.project.teams.all():
            team.steps.get_or_create(step=instance)
