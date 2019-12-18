from django import template

register = template.Library()


@register.simple_tag
def link_add_customer(link):
    return "<a href='{}'>Add new</a>".format(link)
