from django.utils import timezone as django_timezone

from datetime import timedelta
from dateutil.relativedelta import relativedelta


def increase_date(days=0, months=0, hours=0, seconds=0, weeks=0, date=None):
    date = django_timezone.now() if date is None else date
    date += timedelta(days=days, hours=hours, seconds=seconds, weeks=weeks)
    if months:
        date += relativedelta(months=months)
    return date
