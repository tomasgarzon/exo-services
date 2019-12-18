from celery import Task

from django.conf import settings

from utils.dates import string_to_datetime
from ..hubspot.contact import (
    Contact,
    HubSpotException,
)


class CreateHubspotContactTask(Task):
    name = 'CreateHubspotContactTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        email = kwargs.get('email')
        entry_point = kwargs.get('entry_point')
        city = kwargs.get('city', None)
        interested_join = kwargs.get('interested_join', None)

        contact = Contact(
            full_name='{} {}'.format(first_name, last_name),
            email=email,
            interested_joining_the_community=interested_join,
            onboarding_entry_point=entry_point,
            summit_city=city)
        contact.update_or_create_contact()


class HubspotContactConvertToMemberTask(Task):
    name = 'HubspotContactConvertToMemberTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        email = kwargs.get('email')
        contact = Contact(email=email)
        try:
            contact.convert_contact_to_member()
        except HubSpotException:
            self.retry(countdown=60, max_retries=3)


class HubspotContactAddCertificationTask(Task):
    name = 'HubspotContactAddCertificationTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        email = kwargs.get('email')
        certification_name = kwargs.get('certification_name')
        contact = Contact(email=email)
        try:
            contact.set_certification(certification_name)
        except HubSpotException:
            self.retry(countdown=60, max_retries=3)


class HubspotUpdateContactEmailTask(Task):
    name = 'HubspotUpdateContactEmailTask'
    ignore_results = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        old_email = kwargs.get('old_email')
        new_email = kwargs.get('new_email')
        hubspot_user = Contact.get_contact(old_email)
        hubspot_user.update_email(new_email)


class HubspotUpdateContactFoundationsDate(Task):
    name = 'HubspotUpdateContactFoundationsDate'
    ignore_result = True

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return
        email = kwargs.get('email')
        date = kwargs.get('date')
        contact = Contact.get_contact(email)
        contact.set_foundations_joining_date(string_to_datetime(date))
