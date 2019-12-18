from django import template

register = template.Library()


@register.filter
def role_by_project(role, project):
    labels = project.customize.get('roles').get('labels')
    results = filter(lambda x: x[0] == role.code, labels)
    return next(results)[1]
