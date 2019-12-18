from django.db import models

from ..querysets.qa_session import QASessionQueryset


class QASessionManager(models.Manager):

    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = QASessionQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_advisor(self, user):
        try:
            assert user.is_consultant
        except AssertionError:
            raise Exception('Your do not have permissions')

        return self.get_queryset().filter(members__consultant__user=user)
