import logging
import csv
from dateutil.parser import parse

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from consultant.models import Consultant
from relation.models import ConsultantRoleCertificationGroup, ConsultantRole
from ...certification_helpers import CertificationConsultantRoleWrapper

logger = logging.getLogger('accredible')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', nargs='+', type=str,
            help='ExO {Ambassador | Consultant | Sprint Coach | Trainer | Foundations | Board Advisor} Certification - {Virtual | City}'     # noqa
        )
        parser.add_argument('-w', '--when', nargs='+', type=str)
        parser.add_argument('-f', '--file', nargs='+', type=str)

    def get_emails_from_csv(self, path):
        emails = []
        with open(path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')

            for row in spamreader:
                emails.append(row[0])
        return emails

    def check_consultant_status(self, emails, role):
        status_ok = True

        for email in emails:
            try:
                consultant = Consultant.objects.get(user__emailaddress__email=email)
            except ObjectDoesNotExist:
                status_ok = False
                self.stdout.write(self.style.ERROR(
                    'ERROR: Consultant does not exist: {}'.format(email)),
                )
                break
            if consultant.consultant_roles.filter(
                    certification_role=role,
                    credentials__isnull=False).exists():
                status_ok = False
                self.stdout.write(
                    self.style.ERROR(
                        'ERROR: Consultant already certified: {}'.format(email)
                    )
                )
                break

        return status_ok

    def get_group_consultant_role(
            self, name, when):
        return ConsultantRoleCertificationGroup.objects.get(
            name=name,
            issued_on=when)

    def create_consultant_roles(
            self, emails, consultant_role_group):
        certification_role = consultant_role_group.consultant_roles.first().certification_role
        new_consultant_roles = []
        for email in emails:
            consultant = Consultant.objects.get(
                user__emailaddress__email=email,
            )
            consultant_role, _ = ConsultantRole.objects.update_or_create(
                consultant=consultant,
                certification_role=certification_role,
                defaults={
                    'certification_group': consultant_role_group,
                },
            )
            new_consultant_roles.append(consultant_role)
        return new_consultant_roles

    def update_group_with_new_consultants(
            self, consultant_role_group, consultant_roles):
        consultant_wrapper = CertificationConsultantRoleWrapper()
        consultant_wrapper.update_group_with_more_credentials(
            user_from=consultant_role_group.created_by,
            consultant_role_group=consultant_role_group,
            consultant_roles=consultant_roles)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Command init...'))

        # Params
        file = kwargs.get('file')[0]
        name = kwargs.get('name')[0]
        when = kwargs.get('when')[0]
        when = parse(when)

        # Data
        csv_mails = self.get_emails_from_csv(file)
        consultant_role_group = self.get_group_consultant_role(name, when)
        certification_role = consultant_role_group.consultant_roles.first().certification_role
        status_ok = self.check_consultant_status(csv_mails, certification_role)

        if not certification_role:
            return

        if not csv_mails:
            self.stdout.write(self.style.ERROR('No emails in CSV'))
            return

        if not status_ok:
            return

        new_consultant_roles = self.create_consultant_roles(csv_mails, consultant_role_group)
        self.update_group_with_new_consultants(
            consultant_role_group,
            new_consultant_roles,
        )

        self.stdout.write(self.style.SUCCESS('Command finished'))
