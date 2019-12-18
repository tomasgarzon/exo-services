from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from badge.helpers import update_or_create_badge

from ...models import QASession


class Command(BaseCommand):

    def create_swarm_badge(self, swarms):
        category = settings.EXO_ROLE_CATEGORY_SWARM
        long_description = 'Daily script'

        for swarm in swarms:
            title = swarm.project.name

            for consultant_project_role in swarm.members.all():
                user = consultant_project_role.consultant.user
                code = settings.EXO_ROLE_CODE_SWARM_ADVISOR
                item = {
                    'name': title,
                    'date': swarm.start_at.date()
                }
                update_or_create_badge(
                    user_from=user,
                    user_to=user,
                    code=code,
                    category=category,
                    items=[item],
                    description=long_description)

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating Swarm badges ...')

        swarms = QASession.objects.filter(end_at__date=timezone.now().date())
        self.create_swarm_badge(swarms)

        self.stdout.write(self.style.SUCCESS('Swarm Badges created'))
