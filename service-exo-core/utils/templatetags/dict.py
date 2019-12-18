from django import template
from django.utils.text import slugify

register = template.Library()


@register.filter(name='lookup')
def cut(value, arg):
    return value[arg]


@register.filter(name='lookup_slug')
def cut_slug(value, arg):
    return value[slugify(arg).replace('-', '_')]
