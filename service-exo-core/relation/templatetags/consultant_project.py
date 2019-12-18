from django import template

register = template.Library()


@register.filter
def total_projects(consultant, role=None):
    if role:
        return consultant.get_projects(
            role=role,
        ).count()
    else:
        return consultant.get_projects().count()
