from django.db import models

from exo_area.models import ExOArea


class ConsultantExOAreaManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True

    def update_from_values(self, consultant, exo_areas):
        for exo_area in exo_areas:
            self.get_or_create(
                consultant=consultant,
                exo_area=ExOArea.objects.get(code=exo_area),
            )
        # remove unselected
        self.get_queryset().filter(consultant=consultant).exclude(exo_area__code__in=exo_areas).delete()
