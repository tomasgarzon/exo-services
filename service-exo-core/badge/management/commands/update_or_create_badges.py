from django.core.management.base import BaseCommand

from exo_role.models import Category

from ...models import Badge
from ...conf import settings


class Command(BaseCommand):

    def _create_badge(self, code, category, order):

        return Badge.objects.update_or_create(
            code=code,
            category=category,
            defaults={
                'order': order
            }
        )

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating badges ...'))

        Badge.objects.exclude(
            category=settings.BADGE_CATEGORY_COMMUNITY).delete()
        index = 1

        for category in Category.objects.all():
            for role in category.roles.all():
                self._create_badge(role.code, category.code, index)
            index += 1

        for code in dict(settings.BADGE_CODE_COMMUNITY_CHOICES).keys():
            self._create_badge(code, settings.BADGE_CATEGORY_COMMUNITY, 6)

        self.stdout.write(self.style.SUCCESS('Badges created'))
