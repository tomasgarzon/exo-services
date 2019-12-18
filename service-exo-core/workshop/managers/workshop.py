from project.managers.project import ProjectManager
from project.models.mixins import ProjectCreationMixin

from ..querysets.workshop import WorkshopQuerySet


class WorkshopManager(ProjectManager, ProjectCreationMixin):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = WorkshopQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
