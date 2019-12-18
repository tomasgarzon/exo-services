from django import template

register = template.Library()


@register.simple_tag
def position_display(user):
    position = user.position
    company = user.company
    if not company:
        return position
    return '{} at {}'.format(position, company)


@register.simple_tag
def get_industry_level(value):
    level = None

    if value == 5:
        level = 'Expert'
    elif value == 4:
        level = 'Very advanced'
    elif value == 3:
        level = 'Advanced'
    elif value == 2:
        level = 'Medium'
    elif value == 1:
        level = 'Beginner'

    return level


@register.simple_tag(takes_context=True)
def public_email(context, user, show_original=False):
    return user.email


@register.filter(name='http')
def http(value):
    if not value.startswith('http'):
        return 'http://' + value
    return value
