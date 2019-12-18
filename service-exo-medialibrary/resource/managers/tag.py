from django.db import models

from ..querysets.tag import TagQueryset
from ..conf import settings


class TagManager(models.Manager):
    queryset_class = TagQueryset
    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_name(self, name):
        return self.get_queryset().filter_by_name(name)

    def get_development_tag(self):
        return self.get_or_create(name=settings.RESOURCE_DEVELOPMENT_TAG_NAME)

    def create_tags_vimeo(self, tags):
        vimeo_tags = []
        for tags_json in tags:
            name = tags_json.get('name', None)
            defaults = {'extra_data': tags_json}
            tag, _ = self.get_or_create(name=name, defaults=defaults)
            vimeo_tags.append(tag)
        return vimeo_tags

    def add_tags_to_resource(self, tags, resource):
        for tag in tags:
            resource.tags.add(tag)
