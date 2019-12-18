import csv
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from exo_accounts.models import EmailAddress

from ...models import ExOCertification, CertificationRequest


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file', nargs='+', type=str, help='CSV file with information from deals')

    def get_level(self, level):
        LEVEL_MAPPING = {
            'level_2': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'level_2_ft': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A,
            'level_3': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
        }
        return LEVEL_MAPPING.get(level)

    def handle(self, *args, **kwargs):
        path = kwargs.get('file')[0]

        with open(path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for row in spamreader:
                deal_id = row[6]
                try:
                    str_email = row[0].split(' ')[-1:][0]
                    email = EmailAddress.objects.get(email=str_email)
                    certification = ExOCertification.objects.get(level=self.get_level(row[1]))
                    user = email.user
                    data = {
                        'certification': certification,
                        'price': row[3],
                        'created': datetime.strptime(row[5], '%m/%d/%Y'),
                        'status': settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
                        'user': user,
                        'requester_email': str_email,
                        'requester_name': user.full_name,
                    }

                    certification_request, created = CertificationRequest.objects.get_or_create(
                        hubspot_deal=deal_id,
                        defaults=data,
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS('Deal [{}]: Successfully created {}'.format(
                                deal_id, certification_request)
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('Deal [{}]: Already exists CertRequest {}'.format(
                                deal_id, certification_request)
                            )
                        )
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR('Deal [{}]: Errored {}'.format(deal_id, exc)))
