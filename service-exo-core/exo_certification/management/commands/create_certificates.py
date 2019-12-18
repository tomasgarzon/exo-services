import csv

from dateutil.parser import parse

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.conf import settings

from consultant.models import Consultant
from exo_role.models import CertificationRole
from relation.models import ConsultantRoleCertificationGroup, ConsultantRole

from ...certification_helpers import CertificationConsultantRoleWrapper


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-n', '--name', nargs='+', type=str,
            help='ExO {Ambassador | Consultant | Sprint Coach | Trainer | Foundations | Board Advisor} Certification - {Virtual | City}}'     # noqa
        )
        parser.add_argument(
            '-c', '--course_name', nargs='+', type=str,
            help='ExO {Ambassador | Consultant | Sprint Coach | Trainer | Foundations | Board Advisor}'
        )
        parser.add_argument(
            '-t', '--type', nargs='+', type=str,
            help='{consultantrole-ambassador | consultantrole-consultant | consultantrole-sprint-coach | consultantrole-exo-trainer | consultantrole-foundations | consultantrole-board-advisor}'   # noqa
        )
        parser.add_argument('-d', '--description', nargs='+', type=str)
        parser.add_argument('-u', '--user_from', nargs='+', type=str)
        parser.add_argument('-f', '--file', nargs='+', type=str)
        parser.add_argument('-i', '--issued_on', nargs='+', type=str)

    def get_emails_from_csv(self, path):
        emails = []
        with open(path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')

            for row in spamreader:
                emails.append(row[0])
        return emails

    def get_role_code(self, _type):
        role_code = None
        roles_dict = {
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_AMBASSADOR: settings.EXO_ROLE_CODE_CERTIFICATION_AMBASSADOR,     # noqa
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_EXO_CONSULTANT: settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,     # noqa
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_COACH: settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,   # noqa
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_EXO_TRAINER: settings.EXO_ROLE_CODE_CERTIFICATION_TRAINER,   # noqa
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_EXO_FOUNDATIONS: settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,  # noqa
            settings.CERTIFICATION_CH_GROUP_CONSULTANT_ROLE_BOARD_ADVISOR: settings.EXO_ROLE_CODE_CERTIFICATION_BOARD_ADVISOR,  # noqa
        }

        if _type not in roles_dict.keys():
            msg = 'Type error, these are the options available: {}'.format(
                roles_dict.keys())
            self.stdout.write(self.style.WARNING(msg))
            return role_code

        return roles_dict.get(_type)

    def check_consultant_status(self, emails, role):
        status_ok = True
        for email in emails:
            try:
                consultant = Consultant.objects.get(
                    user__emailaddress__email=email)
            except ObjectDoesNotExist:
                status_ok = False
                self.stdout.write(self.style.ERROR(
                    'ERROR: Consultant does not exist: {}'.format(email)),
                )
                break
            if consultant.consultant_roles.filter(
                    certification_role=role, credentials__isnull=False).exists():
                status_ok = False
                self.stdout.write(
                    self.style.ERROR(
                        'ERROR: Consultant already certified: {}'.format(email)
                    )
                )
                break

        return status_ok

    def create_consultant_role_group(
            self, user_from, name, description, issued_on, _type):
        data = {
            'name': name,
            'description': description,
            '_type': _type,
            'created_by': user_from,
            'issued_on': issued_on
        }
        return ConsultantRoleCertificationGroup.objects.create(**data)

    def create_consultant_roles(
            self, emails, role_code, consultant_role_group):
        certification_role = CertificationRole.objects.get(code=role_code)

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

    def create_group_and_credentials_accredible(
            self, consultant_role_group, course_name):
        consultant_wrapper = CertificationConsultantRoleWrapper()
        consultant_wrapper.create_group_and_credentials(
            user_from=consultant_role_group.created_by,
            consultant_role_group=consultant_role_group,
            course_name=course_name)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Command init...'))
        # Params
        file = kwargs.get('file')[0]
        name = kwargs.get('name')[0]
        course_name = kwargs.get('course_name')[0]
        description = kwargs.get('description')[0]
        user_from_email = kwargs.get('user_from')[0]
        _type = kwargs.get('type')[0]
        issued_on = kwargs.get('issued_on')[0]
        issued_on = parse(issued_on)

        if not settings.ACCREDIBLE_ENABLED:
            self.stdout.write(
                self.style.WARNING('Accredible integration is not enabled'),
            )

        # Data
        role_code = None
        user_from = get_user_model().objects.get(email=user_from_email)
        csv_mails = self.get_emails_from_csv(file)
        role_code = self.get_role_code(_type)
        role = CertificationRole.objects.get(code=role_code)
        status_ok = self.check_consultant_status(csv_mails, role)

        if not role_code:
            return

        if not csv_mails:
            self.stdout.write(self.style.ERROR('No emails in CSV'))
            return

        if not status_ok:
            return

        consultant_role_group = self.create_consultant_role_group(
            user_from,
            name,
            description,
            issued_on,
            _type,
        )

        self.create_consultant_roles(csv_mails, role_code, consultant_role_group)   # noqa
        self.create_group_and_credentials_accredible(
            consultant_role_group,
            course_name,
        )

        self.stdout.write(self.style.SUCCESS('Command finished'))
