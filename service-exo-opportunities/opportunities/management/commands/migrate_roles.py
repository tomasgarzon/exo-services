from django.core.management.base import BaseCommand
from django.conf import settings

import csv
from exo_role.models import Category, ExORole, CertificationRole

from ...models import Opportunity
from ...certification_helper import CERTIFICATION_REQUIREMENTS


def get_certifications(obj):
    code = obj.code
    return CERTIFICATION_REQUIREMENTS.get(code, [])


def is_other(obj):
    return obj.code in [
        settings.EXO_ROLE_CODE_OTHER_OTHER,
        settings.EXO_ROLE_CODE_SPRINT_OTHER,
    ]


class Command(BaseCommand):
    help = (
        'MIgrate roles in production'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--filename', nargs='+', type=str,
            help='CSF file'
        )

    def handle(self, *args, **options):
        self.stdout.write('\n Migrating opportunities roles: \n\n')
        filename = options.get('filename')[0]

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    opp = Opportunity.objects.get(id=row.get('ID'))
                except Opportunity.DoesNotExist:
                    self.stdout.err('Opp {} does not exist'.format(row.get('ID')))
                    continue
                if opp.is_draft:
                    continue
                category = Category.objects.get(name=row.get('Project type'))
                exo_role = ExORole.objects.get(
                    name=row.get('Role').replace('ExO ', ''), categories=category)
                certification_code = get_certifications(exo_role)
                try:
                    certification_required = CertificationRole.objects.get(
                        code=certification_code[0])
                except IndexError:
                    certification_required = None
                other_role_name = None
                if is_other(exo_role):
                    other_role_name = row.get('Role name')
                opp.exo_role = exo_role
                opp.certification_required = certification_required
                opp.other_role_name = other_role_name
                opp.save()
