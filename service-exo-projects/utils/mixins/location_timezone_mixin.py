import pytz

from django.db import models

from timezone_field.fields import TimeZoneField as ExternalTimeZoneField

from ..dates import get_timezone_utc_relative


class TimeZoneField(ExternalTimeZoneField):
    CHOICES = [(pytz.timezone(tz), tz) for tz in pytz.all_timezones]


class TimezoneMixin(models.Model):
    timezone = TimeZoneField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_timezone_utc_relative(self):
        return get_timezone_utc_relative(self.timezone) if self.timezone else ''


class LocationMixin(models.Model):
    location = models.CharField(blank=True, null=True, max_length=255)
    place_id = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        abstract = True

    def get_country(self):
        country = ''
        try:
            location_split = self.location.split(', ')
            return location_split[len(location_split) - 1] if len(location_split) else ''
        except (IndexError, AttributeError):
            pass
        return country
