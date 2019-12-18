# -*- coding: utf-8 -*-
import pytz

from django import template
from django.utils.formats import date_format

from dateutil import parser


register = template.Library()


CUSTOM_FORMATS = {
    'DATE_FULL': 'l, j F',
    'TIME_FULL': 'H:i',
    'WEEK_DAY': 'l',
    'DAY_AND_MONTH': 'j F',
}


@register.filter(expects_localtime=True)
def format_date(date_parsed, my_format):
    format_resolved = get_format_value(my_format)
    date_final = date_format(
        date_parsed, format=format_resolved, use_l10n=True,
    )
    return date_final


@register.filter
def date_parsed(date):
    try:
        date_parsed = pytz.utc.localize(parser.parse(date))
    except ValueError:
        date_parsed = parser.parse(date)
    return date_parsed


def get_format_value(format_name):
    return CUSTOM_FORMATS.get(format_name)
