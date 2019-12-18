import requests
from django.conf import settings

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from rest_framework.reverse import reverse

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Measures the API response time'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-u', '--url', nargs='+', type=str,
            help='Endpoint to check'
        )
        parser.add_argument(
            '-t', '--token', nargs='+', type=str,
            help='Bearer token (for protected endpoints)'
        )

    def handle(self, *args, **options):
        token = options.get('token', None)
        url = options.get('url', None)
        if url:
            url = url[0]
        else:
            url = '{}{}'.format(
                settings.EXOLEVER_HOST,
                reverse('api:opportunity-list')
            )

        self.stdout.write('\nTesting endpoint: {}'.format(url))
        if token:
            headers = {'Authorization': 'Bearer {}'.format(token[0])}
            res = requests.get(url, headers=headers)
        else:
            res = requests.get(url)
        print('Total objects {}'.format(len(res.json())))
        if res.ok:
            message = self.style.SUCCESS(
                '[Status: {}] Response time {} seconds'.format(
                    res.status_code, res.elapsed.total_seconds()
                )
            )
        else:
            message = self.style.ERROR(
                '[Status: {}] {}'.format(
                    res.status_code,
                    res.json()
                )
            )

        self.stdout.write(message)
