import datetime as _datetime
import pytz
import requests

from django.utils import timezone as django_timezone
from django.utils import formats
from django.conf import settings

from dateutil import parser
from dateutil.relativedelta import relativedelta

from datetime import date, datetime, timedelta, time


def _is_naive(date):
    """
     Date is NAIVE if has NO timezone
    """
    try:
        return date.tzinfo is None or date.tzinfo.utcoffset(date) is None
    except AttributeError:
        return True


def _aware_date(date_time, time_zone=None):
    """
        Add UTC timezon info to date if is a Naive date
        - date
    """
    if _is_naive(date_time):
        if time_zone:
            date_time = time_zone.localize(date_time)
        else:
            date_time = pytz.utc.localize(date_time)
    elif time_zone:
        date_time = time_zone.normalize(date_time)

    return date_time


def localize_date(date, time_zone=None):
    """
        Localize date with city location:
            - date: date any type of date (DateTime, Date)
            - time_zone: pytz timezone object

        If the date has no TZ info, will be used as UTC date
    """
    if not isinstance(date, _datetime.datetime):
        date = datetime.combine(date, time.min)

    if time_zone is None:
        date = _aware_date(date)
    else:
        date = _aware_date(date, time_zone)

    return date


def format_date(date, custom_format):
    if date:
        date = formats.date_format(date, custom_format)
    return date


def string_to_datetime(string_date, custom_timezone=None, custom_format=None):
    string_datetime = parser.parse(string_date)
    if custom_timezone:
        if type(custom_timezone) == str:
            custom_timezone = string_to_timezone(custom_timezone)
        string_datetime = string_datetime.replace(tzinfo=custom_timezone)
    else:
        string_datetime = string_datetime.replace(tzinfo=django_timezone.utc)

    if custom_format:
        string_datetime = string_datetime.strftime(custom_format)

    return string_datetime


def string_to_date(string_date):
    return parser.parse(string_date).date()


def string_to_timezone(string_timezone):
    return pytz.timezone(string_timezone)


def build_datetime(when, timezone='Europe/Madrid', custom_format=None):
    timezone = string_to_timezone(timezone)
    when_as_timezone = when.astimezone(timezone)
    if custom_format:
        return when_as_timezone.strftime(custom_format)
    else:
        return when_as_timezone.isoformat()


def generate_dates(
        start_date, dates_number, lapse, timezone,
        lapse_units=1, start_weeks_monday=True, skip_weekends=False):
    """
    Generate PAIRS of dates according with params configuration
        start_date: date type format
        dates_number: Number of dates
        lapse: weeks, months days
        timezone: timezone for ending dates
        lapse_units: number of units between dates
        start_weeks_monday: force to start weeks on monday
        skip_weekends: skip weekend days
    """
    if type(timezone) == str:
        timezone = string_to_timezone(timezone)

    if type(start_date) == str:
        start_date = string_to_datetime(start_date)
        start_date = string_to_timezone('utc').localize(start_date)

    dates = []
    initial_time = start_date.time()
    dates_start = []

    if lapse == settings.PROJECT_LAPSE_WEEK:
        if start_weeks_monday:
            start_date_step = start_date
            dates_number -= 1
            start_date = iso_to_gregorian(
                start_date.isocalendar()[0],
                # Week number related to year
                start_date.isocalendar()[1] + 1,
                1,
            )
            start_date = datetime.combine(start_date, initial_time)

            if timezone:
                start_date = localize_date(start_date, timezone)

            dates.append((start_date_step, decrease_date(seconds=1, date=start_date)))

        dates_start = [start_date + timedelta(weeks=_) for _ in range(dates_number)]
        step_size = {'weeks': 1}

    elif lapse == settings.PROJECT_LAPSE_DAY:
        # If not skip_weekends always add days
        push_new_date = not skip_weekends

        if skip_weekends:
            crosed_weeks = int(dates_number / 7)
            week_day = start_date.isocalendar()[2]
            jump_week = week_day + dates_number > 5
            # Only one week
            if not crosed_weeks and jump_week:
                dates_number = dates_number + 2
            elif crosed_weeks:
                dates_number = dates_number + (2 * crosed_weeks)

        dates_start = [
            start_date + timedelta(days=_)
            for _ in range(dates_number)
            if push_new_date or (start_date + timedelta(days=_)).date().isocalendar()[2] < 6
        ]
        step_size = {'days': 1}

    dates_start_array = [[step, step + timedelta(**step_size) - timedelta(seconds=1)] for step in dates_start]
    dates += dates_start_array

    return dates


def iso_year_start(iso_year):
    """
    The gregorian calendar date of the first day of the given ISO year
    """
    fourth_jan = date(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday() - 1)
    return fourth_jan - delta


def iso_to_gregorian(iso_year, iso_week, iso_day):
    """
        Gregorian calendar date for the given ISO year, week and day
    """
    year_start = iso_year_start(iso_year)
    return increase_date(days=iso_day - 1, weeks=iso_week - 1, date=year_start)


# Timezone utils

def get_timezone_utc_relative(timezone_obj, from_utc=True):
    """
        Return the timezone UTC date offset
    """
    timezone_obj = string_to_timezone(timezone_obj) if type(timezone_obj) == str else timezone_obj
    timezone_obj = get_timezone(timezone_obj, from_utc)

    return '{},{}'.format(
        timezone_obj.strftime('%z')[0:3],
        timezone_obj.strftime('%z')[3:6],
    )


def get_timezone(timezone_obj, from_utc=True):
    """
        Aware the timezone object with a date
    """
    timezone_obj = string_to_timezone(timezone_obj) if type(timezone_obj) == str else timezone_obj
    timezone_tzinfo = clear_dst(timezone_obj) if from_utc else timezone_obj

    timezone_now = django_timezone.now()
    abbr = timezone_now.replace(tzinfo=timezone_tzinfo)

    return abbr


def find_timezone(place_id):
    url = settings.PLACE_TIMEZONE_URL
    data = {
        'placeid': place_id,
        'key': 'A5GGLDymZ7vCfjjy',
    }
    if not settings.POPULATOR_MODE:
        try:
            return requests.get(url, params=data).json().get('timezone')
        except Exception:
            return 'UTC'
    return 'UTC'


def find_place_id(location):
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    data = {
        'input': location,
        'key': settings.PLACE_KEY,
        'language': 'en',
        'inputtype': 'textquery',
        'fields': 'place_id'
    }
    if not settings.POPULATOR_MODE:
        try:
            return requests.get(url, params=data).json().get('candidates')[0].get('place_id')
        except Exception:
            return ''
    return ''


def find_address(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    data = {
        'placeid': place_id,
        'fields': 'formatted_address',
        'key': settings.PLACE_KEY
    }
    if not settings.POPULATOR_MODE:
        try:
            return requests.get(url, params=data).json()['result']['formatted_address']
        except Exception:
            pass
    return ''


def fix_timezone(start, tz):
    tz = string_to_timezone(tz) if type(tz) == str else tz
    start = start.replace(tzinfo=None)
    return tz.localize(start)


def clear_dst(timezone_obj):
    """
        Transform DST times to CEST or CET for timezone who needs
        More info: https://www.timeanddate.com/time/zones/cest
    """
    return timezone_obj.fromutc(django_timezone.now().replace(tzinfo=timezone_obj)).tzinfo


def increase_date(days=0, months=0, hours=0, seconds=0, weeks=0, date=None):
    date = django_timezone.now() if date is None else date
    date += timedelta(days=days, hours=hours, seconds=seconds, weeks=weeks)
    if months:
        date += relativedelta(months=months)
    return date


def decrease_date(days=0, months=0, hours=0, seconds=0, weeks=0, date=None):
    date = django_timezone.now() if date is None else date
    date -= timedelta(days=days, hours=hours, seconds=seconds, weeks=weeks)
    if months:
        date -= relativedelta(months=months)
    return date
