from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def rating_star(
    name, value, display_name=False, icon='star',
    star_color='yellow',
):
    rating = ''
    if display_name:
        rating = '<label for="%s" class="control-label">%s</label>' % name

    rating = '%s<input id="%s" value="%s" \
                class="rating-loading rate-input" \
                data-starclass="%s">' % (
        rating,
        name,
        value,
        star_color,
    )
    return mark_safe(rating)
