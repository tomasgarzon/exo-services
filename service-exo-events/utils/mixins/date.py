import pytz
from django.utils import timezone as django_timezone


def string_to_timezone(string_timezone):
    return pytz.timezone(string_timezone)


def get_timezone(timezone_obj, from_utc=True):
    """
        Aware the timezone object with a date
    """
    timezone_obj = string_to_timezone(timezone_obj) if type(timezone_obj) == str else timezone_obj
    timezone_tzinfo = clear_dst(timezone_obj) if from_utc else timezone_obj

    timezone_now = django_timezone.now()
    abbr = timezone_now.replace(tzinfo=timezone_tzinfo)

    return abbr


def clear_dst(timezone_obj):
    """
        Transform DST times to CEST or CET for timezone who needs
        More info: https://www.timeanddate.com/time/zones/cest
    """
    return timezone_obj.fromutc(django_timezone.now().replace(tzinfo=timezone_obj)).tzinfo


def get_timezone_utc_relative(timezone_obj, from_utc=True):
    """
        Return the timezone UTC date offset
    """
    timezone_obj = string_to_timezone(timezone_obj) if type(timezone_obj) == str else timezone_obj
    timezone_obj = get_timezone(timezone_obj, from_utc) if from_utc else timezone_obj

    return '{},{}'.format(
        timezone_obj.strftime('%z')[0:3],
        timezone_obj.strftime('%z')[3:6],
    )
