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

    @property
    def timezone_name(self):
        if type(self.timezone) is str:
            return self.timezone
        return self.timezone.zone if self.timezone else ''

    def get_timezone_utc_relative(self):
        return get_timezone_utc_relative(self.timezone) if self.timezone else ''


class LocationTimezoneMixin(TimezoneMixin, models.Model):
    location = models.CharField(blank=True, null=True, max_length=255)
    place_id = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        abstract = True

    def get_country(self):
        return self.country

    def extract_city_country(self):
        city = country = ''
        if self.location:
            if len(self.location.split(',')) > 1:
                city = self.location.split(',')[0]
                country = self.location.split(',')[-1]

            elif len(self.location.split('-')) > 1:
                city = self.location.split('-')[0]
                country = self.location.split('-')[-1]

            else:
                country = self.location

        return {'city': city.lstrip(), 'country': country.lstrip()}

    @property
    def city(self):
        return self.extract_city_country().get('city')

    @property
    def country(self):
        return self.extract_city_country().get('country')
