from django import template

from ..shortcuts import has_project_perms as project_perms
from ..shortcuts import has_team_perms as team_perms
from ..objects import get_team_for_user

register = template.Library()


@register.simple_tag(takes_context=True)
def has_project_perms(context, user, perm, *args, **kwargs):
    """
        kwargs:
            - project: project, if it isn't in context.
            - related: related object for perms check
    """
    project = kwargs.get('project')
    if not project:
        project = context.get('project')
    if not project:
        raise TypeError

    return project_perms(project, perm, user, related=kwargs.get('related'))


@register.simple_tag(takes_context=True)
def has_team_perms(context, team, user, perm, *args, **kwargs):
    """
        kwargs:
            - related: related object for perms check
    """
    return team_perms(team, perm, user, related=kwargs.get('related'))


@register.simple_tag(takes_context=True)
def get_team_perms(context, user, project):
    return get_team_for_user(project, user)


@register.simple_tag(takes_context=True)
def get_granted_users(context, object, permissions=''):
    return object.get_granted_users(permissions.split(','))
