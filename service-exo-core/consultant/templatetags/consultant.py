from django import template

from consultant.search import consultant_settings

register = template.Library()


@register.simple_tag
def consultant_registration_status(consultant):
    status = consultant.status_detail
    return dict(consultant_settings.CONSULTANT_CH_STATUS).get(status, status)


@register.simple_tag
def mark_site_as_checked(consultant, public_site):
    return 'checked' if public_site[0] in consultant.public_sites else ''
