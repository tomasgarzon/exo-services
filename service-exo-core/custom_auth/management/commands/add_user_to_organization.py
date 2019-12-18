from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

from ...models import InternalOrganization


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('organization', type=str)
        parser.add_argument('role', type=str)
        parser.add_argument('position', type=str)

    def handle(self, *args, **options):
        email = options.get('email')
        name = options.get('organization')
        role = options.get('role')
        position = options.get('position')

        user = get_user_model().objects.get(email=email)
        organization = InternalOrganization.objects.get(name=name)
        if role not in [settings.RELATION_ROLE_CH_ADMIN, settings.RELATION_ROLE_CH_REGULAR]:
            role = settings.RELATION_ROLE_CH_REGULAR

        organization.users_roles.get_or_create(
            user=user,
            role=role,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            position=position)
