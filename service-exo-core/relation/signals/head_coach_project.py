def add_head_coach_project(sender, relation, *args, **kwargs):
    consultant = relation.consultant
    user = consultant.user
    relation.project.add_manager_permissions(user)


def remove_head_coach_project(sender, relation, *args, **kwargs):
    consultant = relation.consultant
    user = consultant.user
    project = relation.project

    delete_manager_perms = True

    for consultant_role in consultant.roles.filter(project=project):
        if consultant_role.has_manager_perms:
            delete_manager_perms = False
            break

    if delete_manager_perms:
        relation.project.remove_manager_permissions(user)
