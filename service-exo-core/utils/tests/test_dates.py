import time as _time
import pytz

from django.test import TestCase
from django.utils import timezone as dj_timezone
from django.conf import settings

from datetime import datetime

from utils.dates import localize_date, _is_naive, string_to_datetime, string_to_timezone

from ..dates import (
    generate_dates,
    get_timezone,
    get_timezone_utc_relative
)


class TestDates(TestCase):

    def test_dates_week(self):
        start_date = datetime.strptime(
            'Jun 1 2005 12:10:00', '%b %d %Y %H:%M:%S',
        )
        start_date_end_week = datetime.strptime(
            'Jun 6 2005 12:09:59', '%b %d %Y %H:%M:%S',
        )

        week_number = start_date.isocalendar()[1]
        timezone = pytz.timezone('America/Sao_Paulo')

        dates = generate_dates(
            start_date=start_date,
            dates_number=3,
            lapse=settings.PROJECT_LAPSE_WEEK,
            timezone=timezone,
        )

        first_dates = dates[0]
        # Expected day for the first date of the week
        self.assertEqual(first_dates[0], start_date)
        self.assertEqual(first_dates[1], timezone.localize(start_date_end_week))

        # Next date have to be Jun 6 2005
        june_6 = datetime.strptime(
            'Jun 6 2005 12:10:00', '%b %d %Y %H:%M:%S',
        )
        june_10 = datetime.strptime(
            'Jun 13 2005 12:09:59', '%b %d %Y %H:%M:%S',
        )
        second_dates = dates[1]
        self.assertEqual(second_dates[0], timezone.localize(june_6))
        self.assertEqual(second_dates[1], timezone.localize(june_10))

        # Monday
        self.assertEqual(second_dates[0].isocalendar()[2], 1)
        # Monday before next week
        self.assertEqual(second_dates[1].isocalendar()[2], 1)

        # Week number check
        for _date, week_increment in zip(dates, range(3)):
            self.assertEqual(
                _date[0].isocalendar()[1],
                week_number + week_increment,
            )
            self.assertEqual(
                _date[1].isocalendar()[1],
                week_number + week_increment + 1,
            )

    def test_dates_days(self):
        start_date = string_to_datetime('Jun 1 2005 09:10:00')
        timezone = string_to_timezone('America/Sao_Paulo')

        dates = generate_dates(
            start_date=start_date,
            dates_number=5,
            lapse=settings.PROJECT_LAPSE_DAY,
            timezone=timezone,
        )

        # Expected day
        self.assertEqual(dates[0][0], start_date)
        self.assertEqual(dates[0][1], string_to_datetime('2005, 6, 2, 09:09:59'))

    def test_dates_empty_for_bad_lapse(self):
        start_date = datetime.today()

        dates = generate_dates(
            start_date=start_date,
            dates_number=10,
            lapse='not_real_type',
            timezone=string_to_timezone('America/Sao_Paulo'),
        )

        self.assertEqual(dates, [])

    def test_skip_weekends(self):

        # Jun 1 2005 is Wednesday
        start_date = string_to_datetime('Jun 1 2005 06:10:00')

        dates = generate_dates(
            start_date=start_date,
            dates_number=10,
            lapse=settings.PROJECT_LAPSE_DAY,
            timezone=string_to_timezone('America/Sao_Paulo'),
            skip_weekends=True,
        )

        for _date in dates:
            self.assertTrue(_date[0].isocalendar()[2] < 6)

        dates = generate_dates(
            start_date=start_date,
            dates_number=21,
            lapse=settings.PROJECT_LAPSE_DAY,
            timezone=string_to_timezone('America/Sao_Paulo'),
            skip_weekends=True,
        )

        for _date in dates:
            self.assertTrue(_date[0].isocalendar()[2] < 6)

    def test_is_naive(self):
        today_unawared = datetime.today()
        self.assertTrue(_is_naive(today_unawared))

        today_awared = dj_timezone.now()
        self.assertFalse(_is_naive(today_awared))

    def test_timezone_conversions_timezone(self):
        """
            Test date transformation to differents TimeZones
        """
        today_no_utc = datetime.today()
        self.assertIsNone(today_no_utc.tzinfo)

        localized_date = localize_date(today_no_utc)
        self.assertEqual(localized_date.tzinfo, pytz.utc)

        # Date with timezone info

        today_utc = dj_timezone.now()

        self.assertIsNotNone(today_utc.tzinfo)

        localized_date = localize_date(today_utc)

        self.assertEqual(
            localized_date.tzinfo,
            today_utc.tzinfo,
        )

    def test_timezone_conversion_to_city_timezone(self):
        """
            Test timezone conversion to city timezone
        """
        time_format = '%H:%M:%S'
        date_format = '%d/%m/%Y'
        FMT = '{} {}'.format(date_format, time_format)

        # Test with America Timezone

        washington_DC_timezone = 'America/New_York'     # UTC -5
        city_timezone = string_to_timezone(washington_DC_timezone)

        used_time = '10:30:00'
        washington_time = '06:30:00'
        used_date = '20/10/2017'

        date_no_utc = datetime.strptime('{} {}'.format(used_date, used_time), FMT)
        date_utc = localize_date(date_no_utc)
        date_relative_city = localize_date(date=date_utc, time_zone=city_timezone)

        diff = date_utc - date_relative_city

        self.assertEqual(diff.days, 0)
        self.assertEqual(diff.total_seconds(), 0.0)

        self.assertEqual(
            date_utc.strftime(time_format),
            used_time,
        )
        self.assertEqual(
            date_utc.strftime(date_format),
            used_date,
        )

        self.assertEqual(
            date_relative_city.strftime(time_format),
            washington_time,
        )
        self.assertEqual(
            date_relative_city.strftime(date_format),
            used_date,
        )

        # Test with Asia Timezone

        city_timezone = string_to_timezone('Asia/Dubai')  # UTC+4
        used_time = '23:00:00'
        used_date = '20/10/2017'
        abu_dhabi_time = '03:00:00'
        abu_dhabi_date = '21/10/2017'
        date_no_utc = datetime.strptime('{} {}'.format(used_date, used_time), FMT)
        date_utc = localize_date(date_no_utc)
        date_relative_city = localize_date(date=date_utc, time_zone=city_timezone)

        self.assertEqual(
            date_utc.strftime(time_format),
            used_time,
        )
        self.assertEqual(
            date_utc.strftime(date_format),
            used_date,
        )

        self.assertEqual(
            date_relative_city.strftime(time_format),
            abu_dhabi_time,
        )
        self.assertEqual(
            date_relative_city.strftime(date_format),
            abu_dhabi_date,
        )

        # Test with Asia Timezone and Los Angeles

        city_abu_dhabi_timezone = string_to_timezone('Asia/Dubai')  # UTC+4
        city_california_timezone = string_to_timezone('America/Los_Angeles')  # UTC -8
        abu_dhabi_time = '03:00:00'
        abu_dhabi_date = '23/08/2017'
        california_time = '16:00:00'
        california_date = '22/08/2017'

        date_no_utc = datetime.strptime('{} {}'.format(abu_dhabi_date, abu_dhabi_time), FMT)
        date_abu_dhabi = localize_date(
            date=date_no_utc,
            time_zone=city_abu_dhabi_timezone,
        )
        date_california = localize_date(
            date=date_abu_dhabi,
            time_zone=city_california_timezone,
        )

        self.assertEqual(
            date_abu_dhabi.strftime(time_format),
            abu_dhabi_time,
        )
        self.assertEqual(
            date_abu_dhabi.strftime(date_format),
            abu_dhabi_date,
        )

        self.assertEqual(
            date_california.strftime(time_format),
            california_time,
        )
        self.assertEqual(
            date_california.strftime(date_format),
            california_date,
        )

    def test_get_timezone_utc_relative(self):
        spain_tz = string_to_timezone('Europe/Madrid')
        tokyo_tz = string_to_timezone('Asia/Tokyo')
        transition_times = spain_tz._utc_transition_times
        years = [dj_timezone.now().year, dj_timezone.now().year - 1]
        dst_offset = 3600   # Default offset in seconds
        tz_transitions = [
            (index, k) for index, k in enumerate(transition_times)
            if k.year in years]

        for index, tz_transition in enumerate(tz_transitions):
            if dj_timezone.now() < pytz.utc.localize(tz_transition[1]):
                dst_offset = spain_tz._transition_info[tz_transitions[index - 1][0]][0]
                dst_offset = dst_offset.seconds

        dst_offset = int(dst_offset / 3600)

        utc_offset = get_timezone_utc_relative(spain_tz)
        self.assertEqual(len(utc_offset), 6)
        self.assertEqual(utc_offset, '+0{},00'.format(dst_offset))

        utc_offset = get_timezone_utc_relative(spain_tz, False)
        self.assertEqual(len(utc_offset), 6)
        self.assertEqual(utc_offset, '-00,15')

        utc_offset = get_timezone_utc_relative(tokyo_tz)
        self.assertEqual(len(utc_offset), 6)
        self.assertEqual(utc_offset, '+09,00')

        utc_offset = get_timezone_utc_relative(tokyo_tz, False)
        self.assertEqual(len(utc_offset), 6)
        self.assertEqual(utc_offset, '+09,{}'.format('00' if _time.daylight else '19'))

    def test_get_timezone(self):
        spain_tz = string_to_timezone('Europe/Madrid')

        spain_tz_obj = get_timezone(spain_tz, False)
        self.assertEqual(spain_tz, spain_tz_obj.tzinfo)

        spain_tz_obj = get_timezone(spain_tz)
        self.assertNotEqual(spain_tz, spain_tz_obj.tzinfo)

        tokyo_tz = string_to_timezone('Asia/Tokyo')
        tokyo_tz_obj = get_timezone(tokyo_tz, False)
        self.assertEqual(tokyo_tz, tokyo_tz_obj.tzinfo)
