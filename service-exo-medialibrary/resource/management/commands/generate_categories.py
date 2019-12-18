import logging

from django.core.management.base import BaseCommand

from ...faker_factories import CategoryFactory
from ...models import Category

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_cats', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        num_cats = kwargs.get("num_cats")[0]
        categories = CategoryFactory.create_batch(size=num_cats)
        Category.objects.create_categories_vimeo(categories)
