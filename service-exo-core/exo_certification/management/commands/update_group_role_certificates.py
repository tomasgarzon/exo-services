import logging
import requests

from django.core.management.base import BaseCommand
from django.conf import settings

from pyaccredible.client import AccredibleWrapper

from relation.models import ConsultantRoleCertificationGroup
from certification.accredible.credentials import parse_group_response


logger = logging.getLogger('accredible')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-g', '--group', nargs='+', type=str, help='Group id')

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Command init...'))

        group_id = kwargs.get('group')[0]
        role_group = ConsultantRoleCertificationGroup.objects.filter(
            certification_groups__accredible_id=group_id).first()

        if not role_group:
            self.stdout.write(self.style.ERROR('No group id found in our database'))
            return

        group = role_group.certification_groups.first()
        client = AccredibleWrapper(key=settings.ACCREDIBLE_API_KEY, server=settings.ACCREDIBLE_SERVER_URL)
        response = client.get_credentials_by_group(group_id)

        if response.status_code == requests.codes.ok:
            parse_group_response(group, response.json().get('credentials'))
            self.stdout.write(self.style.SUCCESS('Command finished'))
        else:
            self.stdout.write(self.style.ERROR('Command failed'))
