from .helpers import update_or_create_badge


def create_user_badge(code, category, project, user):
    log_description = 'Migration for project {}'.format(project.pk)
    item = {
        'name': project.name,
        'date': project.start.date(),
    }
    update_or_create_badge(
        user_from=user,
        user_to=user,
        code=code,
        category=category,
        items=[item],
        description=log_description)


def create_consultant_project_role_badge(consultant_project_role):
    code = consultant_project_role.exo_role.code
    category = consultant_project_role.exo_role.categories.first().code
    user = consultant_project_role.consultant.user
    create_user_badge(code, category, consultant_project_role.project, user)


def create_user_project_role_badge(user_project_role):
    code = user_project_role.exo_role.code
    category = user_project_role.exo_role.categories.first().code
    user = user_project_role.user
    create_user_badge(code, category, user_project_role.project, user)
