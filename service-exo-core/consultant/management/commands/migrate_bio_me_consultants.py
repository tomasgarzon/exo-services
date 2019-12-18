from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q, F


class Command(BaseCommand):

    def handle(self, *args, **options):
        get_user_model().objects.filter(consultant__isnull=False).filter(Q(bio_me__isnull=True) | Q(bio_me='')).update(
            bio_me=F('short_me'))
