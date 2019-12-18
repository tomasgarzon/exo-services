from django import template


register = template.Library()


@register.filter()
def partner_name(relations):
    return relations.values_list('partner__name', flat=True)
