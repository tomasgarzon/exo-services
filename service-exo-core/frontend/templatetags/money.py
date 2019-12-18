from django import template
from django.contrib.humanize.templatetags.humanize import intcomma


register = template.Library()


@register.filter(name='amount')
def show_amount(dollars):
    try:
        dollars = round(float(dollars), 2)
    except TypeError:
        return None
    return '$%s%s' % (intcomma(int(dollars)), ('%0.2f' % dollars)[-3:])
