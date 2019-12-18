import pytz

from timezone_field.fields import TimeZoneField as ExternalTimeZoneField

from ..dates import string_to_timezone


class TimeZoneField(ExternalTimeZoneField):
    CHOICES = [(string_to_timezone(tz), tz) for tz in pytz.all_timezones]
