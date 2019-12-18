from django.db import models

from ..querysets.category import CategoryQueryset


class CategoryManager(models.Manager):
    queryset_class = CategoryQueryset
    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def create_categories_vimeo(self, categories):
        vimeo_categories = []
        for category_json in categories:
            name = category_json.get('name', None)
            defaults = {'extra_data': category_json}
            category, _ = self.get_or_create(name=name, defaults=defaults)
            vimeo_categories.append(category)
        return vimeo_categories

    def add_categories_to_resource(self, categories, resource):
        for category in categories:
            resource.categories.add(category)

    def filter_by_name(self, name):
        return self.get_queryset().filter_by_name(name)
