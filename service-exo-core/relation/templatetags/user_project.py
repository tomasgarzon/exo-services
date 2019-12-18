from django import template

register = template.Library()


@register.simple_tag
def get_projects(user):
    return user.get_projects()


@register.simple_tag
def get_project_role(user, project):
    return user.projects_member.filter(project=project).first()
