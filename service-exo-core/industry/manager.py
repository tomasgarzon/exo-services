from django.db import models


class IndustryManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def update_industries(self, user_from, industries_name):
        industries = []
        for name in industries_name:
            try:
                industry = self.get_queryset().filter(name=name)[0]
            except IndexError:
                industry = self.create(
                    name=name,
                    created_by=user_from,
                    public=False,
                )
            industries.append(industry)
        return industries
