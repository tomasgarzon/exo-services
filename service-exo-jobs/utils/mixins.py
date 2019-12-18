from django.db import models

from timezone_field.fields import TimeZoneField

from utils.dates import get_timezone_utc_relative


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
