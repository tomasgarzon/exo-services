from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response

register = template.Library()


@register.filter(name='render')
def render(template_name):
    content = render_to_response(
        template_name,
        {},
    ).content
    return mark_safe(content)
