from django import template

from ..search.helpers import get_value

register = template.Library()


@register.simple_tag(name='get_field')
def get_field(field):
    available_fields = {
        'name': 'Name',
        'shortline': 'Shortline',
        'location': 'Location',
        'extended_bio': 'Extended Bio',
        'bio': 'Bio',
        'languages': 'Languages',
    }

    if field not in available_fields.keys():
        return None

    return {
        'label': available_fields.get(field),
        'instance_name': field
    }


@register.simple_tag(name='get_value')
def get_consultant_value(consultant, field):
    value = get_value(consultant, field)
    return value
