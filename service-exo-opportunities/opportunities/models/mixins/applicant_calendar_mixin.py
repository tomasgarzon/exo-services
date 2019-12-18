import pytz

from django.utils import timezone

from datetime import timedelta

from dateutil import parser
from icalendar import Calendar, Event
from email.mime.text import MIMEText


class ApplicantCalendarMixin:

    def get_calendar_dates(self):
        start = self.sow.start_date
        end = self.sow.end_date

        if self.sow.timezone:
            tzinfo = self.sow.timezone
        else:
            tzinfo = pytz.UTC

        if self.sow.start_time and (self.opportunity.is_minute or self.opportunity.is_hour):
            start = '{} {}'.format(start.isoformat(), self.sow.start_time.isoformat())
            end = '{} {}'.format(end.isoformat(), self.sow.start_time.isoformat())

            if self.opportunity.is_minute:
                minutes = self.sow.duration_value
            elif self.opportunity.is_hour:
                minutes = self.sow.duration_value * 60

            end = parser.parse(end).replace(tzinfo=tzinfo) + timedelta(minutes=minutes)
            start = parser.parse(start).replace(tzinfo=tzinfo)

        return start, end

    def get_calendar_description(self):
        description = ''

        if self.opportunity.description:
            description = '{}\n'.format(self.opportunity.description)
        if self.opportunity.exo_role:
            description += 'Role: {}\n'.format(self.opportunity.exo_role.name)
        if self.opportunity.entity:
            description += 'Entity: {}\n'.format(self.opportunity.entity)

        return description

    def get_calendar_event(self):
        cal = Calendar()
        cal.add('prodid', str(self.pk))
        cal.add('version', '2.0')

        start, end = self.get_calendar_dates()
        description = self.get_calendar_description()

        event = Event()
        event.add('uid', str(self.pk))
        event.add('summary', self.opportunity.title)
        event.add('description', description)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', timezone.now())

        if self.sow.location_string:
            event.add('location', self.sow.location_string)

        event.add('status', 'CONFIRMED')

        cal.add_component(event)

        return cal

    def get_ics_event(self):
        ics = None

        if self.has_sow and self.sow.start_date and self.sow.end_date:
            icalstream = self.get_calendar_event()
            ics = MIMEText(icalstream.to_ical().decode('utf-8'), 'calendar')
            ics.add_header('Filename', 'invite.ics')
            ics.add_header('Content-Disposition', 'attachment; filename=invite.ics')
        return ics
