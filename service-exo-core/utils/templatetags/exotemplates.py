from __future__ import unicode_literals

import logging

from django import template


logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(is_safe=False)
def exo_pluralize(value, model=''):
    """
    Returns a plural suffix if the value is not 1.

    If an argument is provided, that string is used instead:

    * If value is 0, class{{ value|pluralize:"es" }} displays "0 {{class_verbose_name_plural}}".
    * If value is 1, class{{ value|pluralize:"es" }} displays "1 {{class_verbose_name}}".
    * If value is 2, class{{ value|pluralize:"es" }} displays "2 {{class_verbose_name_plural}}".

    """
    singular_suffix = model._meta.verbose_name if model else ''
    plural_suffix = model._meta.verbose_name_plural if model else ''

    try:
        if float(value) != 1:
            return plural_suffix
    except ValueError:  # Invalid string that's not a number.
        pass
    except TypeError:  # Value isn't a string or a number; maybe it's a list?
        try:
            if len(value) != 1:
                return plural_suffix
        except TypeError:  # len() of unsized object.
            pass

    return singular_suffix
