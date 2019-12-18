def when_team_post_save(sender, instance, created, *args, **kwargs):
    if created:
        instance.project.create_team_assignments(team=instance)
    else:
        instance.project.delete_team_assignments_when_team_modified(team=instance)


def when_team_pre_delete(sender, instance, *args, **kwargs):
    instance.project.delete_team_assignments(team=instance)
