from django import template

register = template.Library()


@register.filter(is_safe=False)
def get_range(value):
    """
    Returns a list the length of the value

    Will cast a string to an int
    """
    return list(range(int(value)))
