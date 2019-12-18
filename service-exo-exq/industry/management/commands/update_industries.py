from django.core.management.base import BaseCommand
from django.utils import translation

import os

from ...models import Industry


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILENAME = 'industries.txt'


class Command(BaseCommand):
    help = 'Update industries from file'

    def handle(self, *args, **options):
        filename = os.path.join(BASE_DIR, FILENAME)
        with open(filename) as f:
            industries = f.readlines()
            for index, industry_name in enumerate(industries):
                industry_name, industry_es = industry_name.replace('\n', '').split(',')
                try:
                    industry = Industry.objects.get(
                        pk=index + 1
                    )
                except Industry.DoesNotExist:
                    industry = Industry()
                translation.activate('es')
                industry.name = industry_es
                industry.save()
                translation.activate('en')
                industry.name = industry_name
                industry.save()
