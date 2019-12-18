from django import template
from django.utils import timezone

from utils.dates import format_date

from ..helpers import next_project_url
from ..conversation_helpers import add_user


register = template.Library()


@register.simple_tag(takes_context=True)
def my_projects(context):
    user = context['user']
    return user.get_projects()


@register.filter
def localize_project(date, project):
    if date is None:
        date = timezone.now()
    return date.astimezone(project.timezone) if project.timezone else date.astimezone()


@register.filter
def date_format(date, value):
    return format_date(date, value)


@register.simple_tag(takes_context=True)
def next_url_project(context, project):
    user = context['user']
    url, _ = next_project_url(project, user)
    return url


@register.simple_tag()
def add_project_user(user, project):
    return add_user(user, project)
