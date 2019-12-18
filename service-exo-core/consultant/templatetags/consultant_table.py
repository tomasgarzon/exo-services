from django import template
from django.conf import settings
from django.utils.html import mark_safe

from custom_auth.helpers import UserProfileWrapper
from ..search.helpers import get_fields

register = template.Library()


@register.inclusion_tag('network/tags/network_list_header.html', takes_context=True)
def render_header(context):
    user = context.get('user')
    fields = get_fields()
    return {
        'fields': fields,
        'user': user,
    }


@register.inclusion_tag('network/tags/network_list_row.html', takes_context=True)
def render_row(context, item):
    user = context.get('user')
    fields = get_fields()
    profile_url = UserProfileWrapper(user=item.user).profile_slug_url

    return {
        'fields': fields,
        'consultant': item,
        'profile_url': profile_url,
        'object_pk': item.pk,
        'user': user,
    }


@register.simple_tag
def show_picture(consultant, field):
    field_label = field.get('label').lower()
    if field_label == 'name':
        url = consultant.user.profile_picture.get_thumbnail_url(
            settings.EXO_ACCOUNTS_MEDIUM_IMAGE_SIZE,
            settings.EXO_ACCOUNTS_MEDIUM_IMAGE_SIZE,
        )
        image = """
            <img alt=\"{name}\" title=\"{name}\" class=\"img-circle\"
                src=\"{url}\" />""".format(name=consultant.user.full_name, url=url)
        content = mark_safe("<span class='l-h-34'>{} {}</span>".format(
            image,
            consultant.user.full_name,
        ))
        if not consultant.is_disabled:
            return mark_safe("<a data-action='stop' href='{}'>{}</a>".format(
                UserProfileWrapper(consultant.user).profile_slug_url,
                content,
            ))
        else:
            return content
    elif field_label == 'e-mail':
        return consultant.user.email
    elif field_label == 'location':
        return consultant.user.location or ''
    elif field_label == 'status':
        return consultant.status_detail
