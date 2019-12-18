from django import template

register = template.Library()


@register.filter(name='label_tag')
def label_tag_custom(field, class_name):
    return field.label_tag(attrs={'class': class_name})
