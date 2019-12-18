# django imports
from django import template

import itertools
import datetime
import pytz
import dateutil

register = template.Library()


@register.filter
def group_by_date(dates, timezone):
    tz = pytz.timezone(timezone)
    dates_parser = []
    for day in dates:
        try:
            new_date = pytz.utc.localize(dateutil.parser.parse(day))
        except ValueError:
            new_date = dateutil.parser.parse(day)
        dates_parser.append(new_date)
    days = [
        tz.normalize(day.replace(tzinfo=pytz.utc)) for day in dates_parser
    ]
    days2 = [
        list(group) for k, group in itertools.groupby(
            days, key=datetime.datetime.toordinal,
        )
    ]

    return [(day[0].date, day) for day in days2]
