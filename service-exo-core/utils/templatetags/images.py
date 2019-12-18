from django import template

register = template.Library()


@register.simple_tag
def image_thumbnail_url(field, width, height):
    try:
        image = field.get_thumbnail_url(width, height)
        return image
    except (ValueError, AttributeError):
        return ''
