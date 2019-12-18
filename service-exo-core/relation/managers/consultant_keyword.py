from django.db import models

from .level_mixin import LevelMixin


class ConsultantKeywordManager(LevelMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def update_from_values(self, consultant, keywords, keywords_level=[], delete_previous=True, tag=None):
        if delete_previous:
            if tag:
                consultant.keywords.filter(keyword__tags__name=tag).delete()
            else:
                consultant.keywords.all().delete()

        for value in keywords_level:
            keyword = list(filter(lambda x: x.name == value.get('keyword').get('name'), keywords))[0]
            keyword_level, created = consultant.keywords.update_or_create(
                keyword=keyword,
                defaults={'level': value.get('level')},
            )
