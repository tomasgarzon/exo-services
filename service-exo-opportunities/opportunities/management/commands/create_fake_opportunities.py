from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from datetime import timedelta

from utils.faker_factory import faker
from exo_role.models import ExoRole, CertificationRole

from ...models import Opportunity

User = get_user_model()
CERT_COACH = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
COACH = settings.EXO_ROLE_CODE_SPRINT_COACH


class Command(BaseCommand):
    help = (
        'Create random opportunities'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-n', '--number', nargs='+', type=int,
            help='Number of opportunities to create'
        )
        parser.add_argument(
            '-u', '--uuid', nargs='+', type=str,
            help='User UUID'

        )

    def create_opportunity(self, user):
        data = {
            'title': faker.word(),
            'description': faker.text(),
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'exo_role': ExoRole.objects.get(code=COACH),
            'certification_required': CertificationRole.objects.get(code=CERT_COACH),
            'start_date': timezone.now() + timedelta(days=10),
            'duration': '1 week',
            'keywords': [],
            'entity': faker.company(),
            'questions': [{'title': faker.word()}]
        }
        opportunity = Opportunity.objects.create_opportunity(
            user,
            **data)
        return opportunity

    def handle(self, *args, **options):
        self.stdout.write('\n Creating opportunities for testing: \n\n')
        number_of_opportunities = options.get('number')[0]
        uuid = options.get('uuid')[0]
        user, _ = get_user_model().objects.get_or_create(
            uuid=uuid,
            is_superuser=True,
            is_active=True,
            is_staff=True)
        for _ in range(number_of_opportunities):
            self.create_opportunity(user)
        self.stdout.write('\n Finish!! \n\n')
