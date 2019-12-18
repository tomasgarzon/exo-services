from project.managers.project import ProjectManager

from ..querysets.sprint import SprintQuerySet


class SprintManager(ProjectManager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = SprintQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
