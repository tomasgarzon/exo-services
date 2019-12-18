from django.db import models

from .level_mixin import LevelMixin


class ConsultantIndustryManager(LevelMixin, models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def update_from_values(self, consultant, industries, industries_level=[], delete_previous=True):

        if delete_previous:
            consultant.industries.all().delete()

        for value in industries_level:
            industry = list(filter(lambda x: x.name == value.get('industry').get('name'), industries))[0]
            industry_level, created = consultant.industries.get_or_create(
                industry=industry,
                defaults={'level': value.get('level')},
            )
            if not created:
                industry_level.level = value.get('level')
                industry_level.save()
