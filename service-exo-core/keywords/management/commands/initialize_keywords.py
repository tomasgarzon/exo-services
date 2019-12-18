from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Keyword


class Command(BaseCommand):
    def handle(self, *args, **options):
        exoAttributes = settings.CORE_EXO_ATTRIBUTES
        exoIndustries = list(settings.CORE_CH_INDUSTRIES_LIST)

        for name in exoIndustries + exoAttributes:
            Keyword.objects.get_or_create(
                name=name,
                defaults={'public': True},
            )
