import csv
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from exo_accounts.models import EmailAddress
from exo_certification.tasks import HubspotCertificationDealSyncTask

from ...models import ExOCertification, CertificationRequest


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--file', nargs='+', type=str, help='CSV file')

    def handle(self, *args, **kwargs):
        path = kwargs.get('file')[0]
        certification = ExOCertification.objects.get(level='L2A')
        with open(path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                try:
                    str_email = row[1]
                    email = EmailAddress.objects.get(email=str_email)
                    user = email.user
                    data = {
                        'price': 0,
                        'created': datetime.strptime(row[2], '%Y-%m-%d'),
                        'status': settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DRAFT,
                        'user': user,
                        'requester_email': str_email,
                        'requester_name': user.full_name,
                    }

                    certification_request, created = CertificationRequest.objects.get_or_create(
                        user=user,
                        certification=certification,
                        defaults=data,
                    )
                    if created:
                        HubspotCertificationDealSyncTask().s(pk=certification_request.pk).apply()
                        certification_request.refresh_from_db()
                        self.stdout.write(
                            self.style.SUCCESS('email [{}]: Successfully created {}'.format(
                                str_email, certification_request)
                            )
                        )
                        certification_request.status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED
                        certification_request.save(update_fields=['status'])
                    else:
                        self.stdout.write(
                            self.style.WARNING('email [{}]: Already exists CertRequest {}'.format(
                                str_email, certification_request)
                            )
                        )
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR('email [{}]: Errored {}'.format(str_email, exc)))
